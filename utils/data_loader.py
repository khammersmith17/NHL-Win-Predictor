from typing import List, Mapping, Dict, str
import json
from io import StringIO
import logging 
import requests
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from time import sleep
import os
import sqlite3

logger = logging.getLogger('log')
logging.basicConfig(level=logging.DEBUG)

class DataLoader:
    def __init__(self) -> None:
        self.urls: Mapping[str,str] = json.load(open('../configs/data-urls.json', 'r'))
        if (db_name:= os.getenv("DATABASE_NAME")):
            self.db_name = db_name
        else:
            raise ValueError("Set DATABASE_NAME")
        self.team_id_map = json.load(open("../configs/team-id-map.json", "r"))
        self.team_abbrev_mapping = json.load(open("../configs/team-to-abv-mapping.json", "r"))
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
            43, 46, 50, 44, 47, 25, 38, 37, 33, 34, 32, 30, 29, 58, 59,
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
            cursor.execute(schema)
            db.commit()

        self.fill_team_table()
        data = []
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for team, url in self.urls.items():
                logger.debug(f"loading in {team}")
                data = requests.get(url).content.decode("utf-8")
                reader = csv.reader(StringIO(data))
                next(reader)
                team_name = self.team_abbrev_mapping.get(team)
                team_id = self.team_id_map.get(team_name)
                while int(next(reader)[1]) < 2021:
                    pass
                for row in reader:
                    new_data = [team_id, row[7]]
                    new_data.extend([row[i] for i in self.raw_header_indexes])
                    sql = self.generate_write_sql(data=new_data, table="raw")
                    cursor.execute(sql)
            db.commit()

    def fill_team_table(self):
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for team_id, team_abv in self.team_id_map.items():
                team_name = self.team_abbrev_mapping.get(team_abv);
                cursor.execute(f"""
                INSERT INTO TEAMS
                (team_id, team_name, team_code)
                VALUES ({team_id}, {team_name}, {team_abv}""")
            db.commit()

    def set_yesterday(self):
        yesterday = (
            datetime.now() - timedelta(days=1)
        ).strftime("%Y-%m-%d")
        self._date_filter = yesterday

    def daily_data_load(self):
        self.set_yesterday()
        self.teams_ids_to_update = []
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            for team, url in self.urls.items():
                data = requests.get(url).content.decode("utf-8").splitlines()[0]
                if data[7] == self._date_filter:
                    team_id = self.team_id_map.get(team)
                    self.team_ids_to_update.append(team_id)
                    new_data = [team_id, self._date_filter]
                    new_data.extend(
                        [data[i] for i in self.raw_header_indexes]
                    )
                    sql = self.generate_write_sql(data=new_data, table="raw")
                    cursor.execute(sql)
            db.commit()

        self.write_averages()
        self.write_model_scores()

    def write_averages(self):
        write_date = datetime.now().strftime("Y-%m-%d")
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

    def write_model_scores(self):
        pass

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
                INSERT INTO TABLE {table_name}
                VALUES ({meta} 
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
                        VALUES ({'.'.join(data)};"""

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
    def daily_load():
        today = datetime.datetime.today()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
        # getting all the utilities needed
        yest_games = requests.get(f"https://api-web.nhle.com/v1/score/{yesterday}").json().get("games")
        team_id_map = json.load(open("../config/team-id-map.json", "r"))
        fields_indexes = json.load(open("../configs/fields-and-indexs.json", "r"))
        conn = psycopg.Connection.connect("Add connection params")
    
        # getting the teams that played the previous day from the response from the NHL API
        teams = set()
        for game in yest_games:
            teams.add(game.get("homeTeam").get("default"))
            teams.add(game.get("awayTeam").get("default"))
    
        urls = {team: url for team, url in json.load(open("../configs/data-urls.json", "r")).items()  if team in teams}
    
    
        for team, url in urls.items():
            data = requests.get(url).content.decode("utf-8").splitlines()
    
            #grabbing the latest updated record that is for situation all
            new_row = None
            i = -1
            while not new_row:
                if data[i].split(",")[8] == "all":
                    new_row = data[i].split() 
            del data
    
            #getting the data we care about from the new data record
            new_data = [team_id_map.get(team), yesterday]
            for header in fields_indexes.get("headers"):
                new_data.append(new_row[fields_indexes.get("index_mappings").get(header)])
    
    
            """
            Writing new data to the raw table
            Getting the last 10 rows from the raw table to generated the new average
            computing the new averages
            writing the new averages to the average table
            """
            with conn.cursor() as cursor:
                cursor.execute(generate_write_sql(table="raw"),tuple(new_data))
                cursor.commit()
    
                query = cursor.execute(f"""
                SELECT * FROM raw_game_stats 
                WHERE team_id = {team_id_map.get(team)} 
                ORDER BY game_date DESC
                LIMIT 10;""")
                result = query.fetch_all()
            avgs = []
            for i in range(len(result[0])):
                curr = []
                for j in range(len(result)):
                    curr.append(result[i][j])
                cur = np.array([curr])
                avgs.append(cur.avg)
            write_date = datetime.datetime.today().strftime("%Y-%m-%d")
            agg_method = 10
            avg_data = [team_id_map.get(team), write_date, agg_method]
            avg_data.extend(avgs)
            with conn.cursor() as cursor:
                cursor.execute(generate_write_sql(table="avg"), tuple(avg_data))
                cursor.commit()
    
        games = requests.get(f"https://api-web.nhle.com/v1/schedule/{today}").get("gameWeek")[0].get("games")
    
        for game in games:
            game_id = game.get("id")
            home_team = game.get("homeTeam").get("placeName").get("default")
            away_team = game.get("awayTeam").get("placeName").get("default")
    
            home_id = team_id_map.get(home_team)
            away_id = team_id_map.get(away_team)
    
            with conn.cursor() as cursor:
                query = cursor.execute(generate_read_avg_sql(home_id))
                home_stats = query.fetchone()
    
                query = cursor.execute(generate_read_avg_sql(away_id))
    
                away_stats = query.fetchone()
    
            new_stats = [game_id, today]
    
            for i in range(len(home_stats)):
                new_stats.append(home_stats[i] - away_stats[i])
    
            new_stats = tuple(new_stats)
    
            with conn.cursor() as cursor:
                query = cursor.execute(generate_write_sql("prediction"), new_stats)
                cursor.commit()
    
     
