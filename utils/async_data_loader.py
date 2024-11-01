import asyncio
import aiosqlite
from datetime import datetime
from typing import List, Union, Dict
import argparse
from aiohttp import ClientSession, ClientTimeout
import aiofiles
import logging
import json
import os
from inference import ModelScorer
import sqlite3
from xgboost import DMatrix
import numpy as np

logger = logging.getLogger('log')
logging.basicConfig(
    level=logging.DEBUG,
    filename="dev.log",
    filemode="w"
)

class DataLoader:
    def __init__(self):
        self.url = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/all_teams.csv"
        self.urls: Dict[str,str] = json.load(open('../configs/data-urls.json', 'r')).get("data_urls")
        self.game_base_url = "https://api-web.nhle.com/v1/schedule/"
        self.master_url = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/all_teams.csv"
        if (db_name:= os.getenv("DATABASE_NAME")):
            self.db_name = db_name
        else:
            raise ValueError("Set DATABASE_NAME")
        self.team_id_map: Dict[str, str] = json.load(open("../configs/team-id-map.json", "r"))
        self.team_abbrev_mapping: Dict[str, str]  = json.load(open("../configs/team-to-abv-mapping.json", "r"))
        self.attrs: List[str] = [
                "blockedShotAttemptsFor",
                "corsiPercentage",
                "dZoneGiveawaysFor",
                "faceOffsWonFor",
                "fenwickPercentage",
                "flurryAdjustedxGoalsFor",
                "flurryScoreVenueAdjustedxGoalsFor",
                "freezeFor",
                "giveawaysFor",
                "goalsAgainst",
                "highDangerGoalsFor",
                "highDangerShotsFor",
                "highDangerxGoalsFor",
                "hitsFor",
                "lowDangerGoalsFor",
                "lowDangerShotsFor",
                "lowDangerxGoalsFor",
                "mediumDangerGoalsFor",
                "mediumDangerShotsFor",
                "mediumDangerxGoalsFor",
                "missedShotsFor",
                "penalityMinutesFor",
                "penaltiesFor",
                "playContinuedInZoneFor",
                "playContinuedOutsideZoneFor",
                "playStoppedFor",
                "reboundGoalsFor",
                "reboundsFor",
                "reboundxGoalsFor",
                "savedShotsOnGoalFor",
                "savedUnblockedShotAttemptsFor",
                "scoreAdjustedShotsAttemptsFor",
                "scoreAdjustedTotalShotCreditFor",
                "scoreAdjustedUnblockedShotAttemptsFor",
                "scoreFlurryAdjustedTotalShotCreditFor",
                "scoreVenueAdjustedxGoalsFor",
                "shotAttemptsFor",
                "shotsOnGoalFor",
                "takeawaysFor",
                "totalShotCreditFor",
                "unblockedShotAttemptsFor",
                "xFreezeFor",
                "xGoalsFor",
                "xGoalsFromActualReboundsOfShotsFor",
                "xGoalsFromxReboundsOfShotsFor",
                "xGoalsPercentage",
                "xOnGoalFor",
                "xPlayContinuedInZoneFor",
                "xPlayContinuedOutsideZoneFor",
                "xPlayStoppedFor",
                "xReboundsFor"
                ]

        self.raw_header_indexes: List[int] =[
            26, 11, 55, 39, 12, 21, 23, 31, 42, 76, 51, 45, 48, 40, 49,
            43, 46, 50, 44, 47, 25, 38, 37, 33, 34, 32, 30, 29, 58,
            35, 36, 52, 60, 54, 61, 22, 27, 24, 41, 59, 53, 17, 15, 57,
            56, 10, 14, 19, 20, 18, 16
        ]
        self._date_filter = None


    async def produce_data_initial_load(self, queue: asyncio.Queue) -> None:
        logger.debug("Here")
        async with ClientSession(timeout=ClientTimeout(1024)) as session:
            async with session.get(self.url) as response:
                logger.debug("Got response")
                content = response.content
                curr_line = b""
                async for chunk in content.iter_chunked(64):
                    curr_line += chunk
                    if b"\n" in curr_line:
                        split = curr_line.split(b"\n")
                        if len(split) > 2:
                            while len(split) > 1:
                                await queue.put(split[0])
                                split = split[1:]
                            curr_line = split[0]
                        elif len(split) == 2:
                            new_line, curr_line = split
                            await queue.put(new_line)

    async def produce_data_daily_load(self, queue: asyncio.Queue) -> None:
        async with ClientSession(timeout=ClientTimeout(2048)) as session:
            async with session.get(self.url) as response:
                logger.debug("Got response")
                content = response.content
                curr_line = b""
                async for chunk in content.iter_chunked(64):
                    curr_line += chunk
                    if b"/n" in curr_line:
                        split = curr_line.split(b"\n")
                        if len(split) == 2:
                            new_line, curr_line = split
                            new_line = new_line.decode("utf-8").split(",")
                            if new_line == self._date_filter:
                                await queue.put(new_line)
                        else:
                            while len(split) > 1:
                                await queue.put(split[0])
                                split = split[1:]
                            curr_line = split[0]

    async def consume_data_first_load(self, queue: asyncio.Queue):
        while True:
            all_data = await queue.get()
            if int(all_data[1]) >= 2021 and all_data[9] == "all":
                team_abv = all_data[0]
                if team_abv == "ARI":
                    team_abv = "UTA"
                team_name = self.team_abbrev_mapping.get(team_abv)
                assert team_name is not None
                team_id = self.team_id_map.get(team_name)
                new_data = [str(team_id), all_data[7]]
                new_data.extend([all_data[index] for index in self.raw_header_indexes])
                sql = await self.generate_write_sql(data=new_data, table="raw")
                async with aiosqlite.connect(self.db_name) as db:
                    await db.execute(sql)
                    await db.commit()
            queue.task_done()

    async def consume_data_daily_load(self, queue: asyncio.Queue) -> None:
        while True:
            thing = await queue.get()
            logger.debug(thing)
            all_data = thing.decode("utf-8").split(",")
            if int(all_data[1]) >= 2021 and all_data[9] == "all":
                team_abv = all_data[0]
                if team_abv == "ARI":
                    team_abv = "UTA"
                team_name = self.team_abbrev_mapping.get(team_abv)
                assert team_name is not None
                team_id = self.team_id_map.get(team_name)
                new_data = [str(team_id), all_data[7]]
                new_data.extend([all_data[index] for index in self.raw_header_indexes])
                sql = await self.generate_write_sql(data=new_data, table="raw")
                async with aiosqlite.connect(self.db_name) as db:
                    await db.execute(sql)
                    await db.commit()
            queue.task_done()


    async def generate_write_sql(self, data: list, table: str = "raw") -> str:
        assert table in {"raw", "avg"}, "invalid key"

        meta = {
            "raw": "team_id, game_date,",
            "avg": "team_id, write_data, agg_method",
            "prediction": "game_id, write_date, agg_method"
        }.get(table)

        table_name = {
            "raw": "RAW_GAME_STATS",
            "avg": "AVG_GAME_STATS"
        }.get(table)

        return f"""
                INSERT INTO {table_name}
                ({meta} 
                blockedShotAttemptsFor,
                corsiPercentage, 
                dZoneGiveawaysFor, 
                faceOffsWonFor,
                fenwickPercentage,
                flurryAdjustedxGoalsFor,
                flurryScoreVenueAdjustedxGoalsFor,
                freezeFor,
                giveawaysFor,
                goalsAgainst,
                highDangerGoalsFor,
                highDangerShotsFor,
                highDangerxGoalsFor,
                hitsFor,
                lowDangerGoalsFor,
                lowDangerShotsFor,
                lowDangerxGoalsFor,
                mediumDangerGoalsFor,
                mediumDangerShotsFor,
                mediumDangerxGoalsFor,
                missedShotsFor,
                penalityMinutesFor,
                penaltiesFor,
                playContinuedInZoneFor,
                playContinuedOutsideZoneFor,
                playStoppedFor,
                reboundGoalsFor,
                reboundsFor,
                reboundxGoalsFor,
                savedShotsOnGoalFor,
                savedUnblockedShotAttemptsFor,
                scoreAdjustedShotsAttemptsFor,
                scoreAdjustedTotalShotCreditFor,
                scoreAdjustedUnblockedShotAttemptsFor,
                scoreFlurryAdjustedTotalShotCreditFor,
                scoreVenueAdjustedxGoalsFor,
                shotAttemptsFor,
                shotsOnGoalFor,
                takeawaysFor,
                totalShotCreditFor,
                unblockedShotAttemptsFor,
                xFreezeFor,
                xGoalsFor,
                xGoalsFromActualReboundsOfShotsFor,
                xGoalsFromxReboundsOfShotsFor,
                xGoalsPercentage,
                xOnGoalFor,
                xPlayContinuedInZoneFor,
                xPlayContinuedOutsideZoneFor,
                xPlayStoppedFor,
                xReboundsFor)
                VALUES ({','.join(data)});"""



    def fill_team_table(self):
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for name, id  in self.team_id_map.items():
                abv = self.team_abbrev_mapping.get(name);
                assert abv is not None
                query =f"""
                INSERT INTO TEAMS
                (team_id, team_name, team_code)
                VALUES ({id}, '{name}', '{abv}')"""
                cursor.execute(query)
            db.commit()

    def set_date(self):
        self._date_filter = datetime.now().strftime("%Y-%m-%d")


async def get_all_data():
    stuff = b""
    async with ClientSession(timeout=ClientTimeout(1000)) as session:
        async with session.get("https://moneypuck.com/moneypuck/playerData/careers/gameByGame/all_teams.csv") as resp:
            response = resp.content
            async with aiofiles.open("test_local2.csv", mode="w") as f:
                async for chunk in response.iter_chunked(64):
                    stuff += chunk
                    await f.write(chunk.decode("utf-8"))
    return stuff

"""
reference function for now
async def main():
    obj = DataLoader()
    queue = asyncio.Queue()
    producer = asyncio.create_task(obj.produce_data(queue))
    consumer = asyncio.create_task(obj.consume_data(queue))

    await asyncio.gather(producer)
    await queue.join()

    consumer.cancel()
"""


async def initial_load():
    data_loader = DataLoader()
    queue = asyncio.Queue()
    producer = asyncio.create_task(data_loader.produce_data_initial_load(queue))
    consumer = asyncio.create_task(data_loader.consume_data_first_load(queue))


    await asyncio.gather(producer)
    await queue.join()

    consumer.cancel()

async def daily_load():
    data_loader = DataLoader()
    data_loader.set_date()

    queue = asyncio.Queue()

    producer = asyncio.create_task(data_loader.produce_data_daily_load(queue))
    consumer = asyncio.create_task(data_loader.consume_data_daily_load(queue))

    await asyncio.gather(producer)
    await queue.join()

    consumer.cancel()

def bool_string_to_bool(value: str):
    if not isinstance(value, str):
        raise TypeError("Argument must be of type str")
    try:
        assert value.lower() == "true" or value.lower() == "false"
    except AssertionError:
        raise ValueError("Accepted values for argument are 'True', 'False'")

if __name__ == "__main__":
    logger.debug("Starting")
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-load", type=bool_string_to_bool, required=True)
    args = parser.parse_args()
    daily_load = args.daily_load

    try:
        if daily_load:
            asyncio.run(initial_load())
        else:
            asyncio.run(daily_load)
    except KeyboardInterrupt:
        pass
