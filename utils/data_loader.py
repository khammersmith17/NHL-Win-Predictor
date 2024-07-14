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

def generate_write_sql(table: str="raw"):
    assert table in {"raw", "avg", "prediction"}, "invalid key"

    meta = {
        "raw": "team_id, game_date,",
        "avg": "team_id, write_data, agg_method",
        "prediction": "game_id, write_date, agg_method"
    }.get(table)

    num_args = {
        "raw": 52,
        "avg": 53,
        "prediction": 53
    }.get(table)

    table_name = {
        "raw": "raw_game_stats",
        "avg": "avg_game_stats",
        "prediction": "prediction_data"
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
                    VALUES ({"%s, "* num_args} %s;""",

def generate_read_avg_sql(team_id: int) -> str:
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
        ORDER BY write_date DESC LIMIT 1;"
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


