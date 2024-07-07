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

logger = logging.getLogger('log')
logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self) -> None:
        self.urls = json.load(open('../configs/data-urls.json', 'r'))
        self.header = None
        self.type_map = None

    def load(self):
        new_data = []
        for team, url in self.urls.items():
            logger.info(f'grabbing data for team: {team}')
            data = requests.get(url).content
            decoded_content = data.decode('utf-8')
            data_csv = csv.reader(decoded_content.splitlines(), delimiter=',')
            for row in data_csv:
                new_data.append(row)
        df = pd.DataFrame(new_data, columns=self.header)
        df = df.astype(self.type_map)
        df_home_team = df[np.logical_and(df.home_or_away == 'HOME', df.situation == 'all')]
        df_away_team = df[np.logical_and(df.home_or_away == 'AWAY', df.situation == 'all')]
        df = pd.merge(right=df_home_team, left=df_away_team, how='inner', on='gameId')
        df.gameDate_x = pd.to_datetime(df.gameDate_x.map(self._to_date))
        self._today()
        df = df[df.gameDate_x > pd.to_datetime(self._date_filter, format="%Y-%m-%d")]
        return df

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

