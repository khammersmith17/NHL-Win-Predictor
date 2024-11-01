from typing import List, Mapping
import json
from io import StringIO
import logging 
import requests
import csv
from inference import ModelScorer
import numpy as np
from datetime import datetime, timedelta
import os
import sqlite3
from xgboost import DMatrix

logger = logging.getLogger('log')
logging.basicConfig(
    level=logging.DEBUG,
    filename="dev.log",
    filemode="w"
)

class DataLoader:
    def __init__(self) -> None:
        self.urls: Mapping[str,str] = json.load(open('../configs/data-urls.json', 'r')).get("data_urls")
        self.game_base_url = "https://api-web.nhle.com/v1/schedule/"
        self.master_url = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/all_teams.csv"
        if (db_name:= os.getenv("DATABASE_NAME")):
            self.db_name = db_name
        else:
            raise ValueError("Set DATABASE_NAME")
        self.team_id_map: Mapping[str, str] = json.load(open("../configs/team-id-map.json", "r"))
        self.team_abbrev_mapping: Mapping[str, str]  = json.load(open("../configs/team-to-abv-mapping.json", "r"))
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
        self.team_ids_to_update = []

    def initial_load(self):
        schema_file = open("../nhl_create_tables.sql", "r")
        schema = schema_file.read()
        schema_file.close()
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for sql in schema.split(";"):
                cursor.execute(sql)
            db.commit()

        self.fill_team_table()
        data = []
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for team, url in self.urls.items():
                logger.debug(f"loading in {team}")
                if team == "Lightning":
                    logger.debug("Skipping lightning")
                    continue
                data = requests.get(url).content.decode("utf-8")
                reader = csv.reader(StringIO(data))
                next(reader)
                team_id = self.team_id_map.get(team)
                while True:
                    year = int(next(reader)[1]) 
                    logger.debug(year)
                    if year >= 2021:
                        break
                for row in reader:
                    new_data = [str(team_id), row[7]]
                    new_data.extend([row[i] for i in self.raw_header_indexes])
                    sql = self.generate_write_sql(data=new_data, table="raw")
                    cursor.execute(sql)
            db.commit()

    def initial_load_v2(self):
        logger.debug("Loading schema")
        schema_file = open("../nhl_create_tables.sql", "r")
        schema = schema_file.read()
        schema_file.close()
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for sql in schema.split(";"):
                cursor.execute(sql)
            db.commit()
        logger.debug("Wrote schema")
        logger.debug("Creating team table")
        self.fill_team_table()

        logger.debug("Making request to get data")
        response = requests.get(self.master_url, stream=True)
        if not response.ok:
            logger.info("Error occured on request, no data today")
        logger.debug("Writing out local temp")
        with open("local_data.csv", "x") as f:
            for data in response.iter_content():
                f.write(data.decode("utf-8"))
        f = open("local_data.csv", "r")
        data_reader = csv.reader(f)
        logger.debug("Got data")
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            next(data_reader)
            row = next(data_reader)
            num_games = 0
            for row in data_reader:
                if int(row[1]) >= 2021 and row[9] == "all":
                    num_games += 1
                    team_abv = row[0]
                    if team_abv == "ARI":
                        team_abv = "UTA"
                    team_name = self.team_abbrev_mapping.get(team_abv)
                    assert team_name
                    team_id = self.team_id_map.get(team_name)
                    assert team_id, f"{team_name}"
                    new_data = [str(team_id), row[7]]
                    new_data.extend([row[i] for i in self.raw_header_indexes])
                    sql = self.generate_write_sql(data=new_data, table="raw")
                    cursor.execute(sql)
            logger.info(f"Commited {num_games} games to db")
            db.commit()

        f.close()
        logger.debug("Deleting temp")
        os.remove("local_data.csv")

    def fill_team_table(self):
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for name, id  in self.team_id_map.items():
                abv = self.team_abbrev_mapping.get(name);
                query =f"""
                INSERT INTO TEAMS
                (team_id, team_name, team_code)
                VALUES ({id}, '{name}', '{abv}')"""
                cursor.execute(query)
            db.commit()

    def set_yesterday(self):
        yesterday = (
            datetime.now() - timedelta(days=1)
        ).strftime("%Y%m%d")
        self._date_filter = yesterday

    def daily_data_load(self):
        self.team_ids_to_update.clear()
        write_date = datetime.now().strftime("Y-%m-%d")
        self.set_yesterday()
        data_stream = requests.get(self.master_url, stream=True)
        if not data_stream.ok:
            logger.info("Error doing data load")
        with open("local_data.csv", "x") as f:
            for b in data_stream.iter_content():
                f.write(b.decode("utf-8"))
        f = open("local_data.csv", "r")
        data_reader = csv.reader(f)
        new_data = list()
        for row in data_reader:
            if row[7] != self._date_filter:
                continue
            else:
                new_data.append(row)


        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for row in new_data:
                team = row[0]
                team_id = self.team_id_map.get(team)
                self.team_ids_to_update.append(team_id)
                new_data = [team_id, self._date_filter]
                new_data.extend(
                    [row[i] for i in self.raw_header_indexes]
                )
                sql = self.generate_write_sql(data=new_data, table="raw")
                logger.info(sql)
                cursor.execute(sql)
            db.commit()
        f.close()

        self.write_averages(write_date=write_date)
        self.write_model_scores(current_date=write_date)

    def write_averages(self, write_date: str):
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for team_id in self.team_ids_to_update:
                query_results = cursor.execute(
                        self.generate_read_avg_sql(team_id)
                    ).fetchall()
                cum_sums = [0] * len(query_results[0])
                for row in query_results:
                    for i in range(len(row)):
                        cum_sums[i] += row[i]
                avgs = [team_id, write_date, len(query_results)]
                avgs.extend([col / len(query_results) for col in cum_sums])
                cursor.execute(self.generate_write_sql(data=avgs, table="avg"))

            db.commit()

    def write_model_scores(self, current_date: str):
        model = ModelScorer()
        todays_games = self.get_todays_games(current_date)
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            home_team_stats = list()
            away_team_stats = list()
            for game in todays_games:
                home_team = game.get("homeTeam")
                assert home_team is not None
                home_team_id = self.team_id_map.get(home_team)
                home_team = cursor.execute(
                f"""
                SELECT * FROM AVG_GAMES_STATS
                WHERE team_id = {home_team_id}
                ORDER BY write_date DESC
                LIMIT 10;
                """).fetchall()
                home_team_stats.append(np.array(home_team[4:]))
                away_team = game.get("awayTeam")
                assert away_team is not None
                away_team_id = self.team_id_map.get(away_team)
                away_team = cursor.execute(
                f"""
                SELECT * FROM AVG_GAMES_STATS
                WHERE team_id = {away_team_id}
                ORDER BY write_date DESC
                LIMIT 10;
                """).fetchall()
                away_team_stats.append(np.array(away_team[4:]))

            scores = list()
            for home, away in zip(home_team_stats, away_team_stats):
                diff = DMatrix(home-away)
                scores.append(model.run_inference(diff))

            for game, pred in zip(todays_games, scores):
                cursor.execute(
                f"""
                INSERT INTO GAME_PREDICTIONS
                game_id, inference_score, agg_method, game_date
                VALUES ({game.get("gameId")}, {pred}, 10, '{current_date}')
                """
                )
            db.commit()

    def generate_write_sql(self, data: List, table: str="raw") -> str:
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

        return   f"""
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

    def generate_read_avg_sql(self, team_id: int) -> str:
        current_reg_season_start = os.getenv("SEASON_START")
        return f"""
            SELECT
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
            xReboundsFor
            FROM avg_game_stats
            WHERE team_id = {team_id}
            AND game_date > DATE({current_reg_season_start})
            ORDER BY write_date DESC LIMIT 10;"
        """
    def get_todays_games(self, current_date: str) -> List[dict]:
        response = requests.get(f"{self.game_base_url}/{current_date}").json()
        return [
            {
                "gameId": game.get("id"),
                "home": game.get("homeTeam").get("placeName").get("default"),
                "away": game.get("awayTeam").get("placeName").get("default")
            }
            for game in response.get("gameWeek").get("games")
        ]




