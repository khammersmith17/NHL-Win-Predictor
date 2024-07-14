from typing import List, Mapping
import json
import io
import logging 
import requests
import csv
import pandas as pd
import numpy as np
import datetime
from time import sleep
import os
import psycopg

logger = logging.getLogger('log')
logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self) -> None:
        self.urls = json.load(open('../configs/data-urls.json', 'r'))
        self.header = None
        self.type_map = None

    def load(self):
        
    @staticmethod
    def _to_date(string):
        return f'{string[0:4]}-{string[4:6]}-{string[6:]}'
    
    def _write(self, df):
        pass

    def _today(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        self._date_filter = yesterday

    def update_data(self):

        while True:
            data = self.load()
            pass



            sleep(60*60*24)

    def generate_raw_data(self):
        df_data = []
        for team, url in self.urls.items():
            logger.info(f"grabbing data for {team}")
            data = requests.get(url).content.decode('utf-8')
            csv_data = csv.reader(data.splitlines(), delimiter=',')
            if not self.header:
                self.header = next(csv_data)
            for i, row in enumerate(csv_data):
                if i == 0:
                    continue
                df_data.append(row)
        df = pd.DataFrame(df_data, columns=self.header)
        df.to_csv("raw-training-data.csv", header=True, index=False)        

def get_full_dataset(year_cut: str=None):
        urls = json.load("../configs/data-urls.json")
        new_data = []
        for team, url in urls.items():
            logger.info(f'grabbing data for team: {team}')
            data = requests.get(url).content
            decoded_content = data.decode('utf-8')
            data_csv = csv.reader(decoded_content.splitlines(), delimiter=',')
            for row in data_csv:
                new_data.append(row)
        df = pd.DataFrame(new_data, columns=header)
        df = df.astype(type_map)
        df_home_team = df[np.logical_and(df.home_or_away == 'HOME', df.situation == 'all')]
        df_away_team = df[np.logical_and(df.home_or_away == 'AWAY', df.situation == 'all')]
        df = pd.merge(right=df_home_team, left=df_away_team, how='inner', on='gameId')
        df.gameDate_x = pd.to_datetime(df.gameDate_x.map(self._to_date))
        self._today()
        df = df[df.gameDate_x > pd.to_datetime(self._date_filter, format="%Y-%m-%d")]
        return df

def generate_sql(table: str="raw"):
    meta = "team_id, game_date," if table == "raw" else "team_id, write_date, agg_method,"
    num_args = 52 if table == "raw" else 53

    return   f"""
            INSERT INTO TABLE RAW_GAME_STATS
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
                    VALUES ({"%s, "*num_args} %s;""",

def daily_load():
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    yest_games = requests.get(f"https://api-web.nhle.com/v1/score/{yesterday}").json().get("games")
    team_id_map = json.load(open("../config/team-id-map.json", "r"))
    fields_indexes = json.load(open("../configs/fields-and-indexs.json", "r"))
    conn = psycopg.Connection.connect("Add connection params")

    teams = set()
    for game in yest_games:
        teams.add(game.get("homeTeam").get("default"))
        teams.add(game.get("awayTeam").get("default"))

    urls = {team: url for team, url in json.load(open("../configs/data-urls.json", "r")).items()  if team in teams}

    for team, url in urls.items():
        data = requests.get(url).content.decode("utf-8").splitlines()

        new_row = None
        i = -1
        while not new_row:
            if data[i].split(",")[8] == "all":
                new_row = data[i].split() 
        new_data = [team_id_map.get(team), yesterday]
        for index in fields_indexes.values():
            new_data.append(new_row[index])

 
        with conn.cursor() as cursor:
            cursor.execute(generate_sql(table="raw"),tuple(new_data))

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
            cursor.execute(generate_sql(table="avg"), tuple(avg_data))
            cursor.commit()

