from enum import Enum
import os
import psycopg
from typing import Tuple

class QueryStatus(Enum):
    SUCCESS = 1
    FAILURE = 0


CONNECTION_STRING = os.get_env("CONNECT_STRING")


class DataInferace:
    def __init__(self):
        self.connection = psycopg.connect(CONNECTION_STRING)

    def write_team_data(self, sql_string: str, data:dict) -> QueryStatus:
        try:
            with self.connection.cursor as cursor:
                #TODO construct sql string
                cursor.execute()
            return QueryStatus.SUCCESS
        except:
            return QueryStatus.FAILURE
    
    def query_team_data(self, team: str) -> Tuple(QueryStatus, dict):
        try:
            with self.conenction.cursor as cursor:
                #TODO construct sql string
                cursor.execute()
                result = cursor.fetch_all()
            return QueryStatus.SUCCESS, result
        except:
            return QueryStatus.FAILURE, None

    def get_average(self, team:str) -> Tuple(QueryStatus, dict):
        try:
            with self.connection.cursor as cursor:
                #TODO construct sql string
                query = ''
                cursor.execute(query)
                result = cursor.fetch_all()
        except:
            return QueryStatus.FAILURE, None

        #TODO compute and return averages

    def write_predictions(self, home_team:str, away_team:str, date: datetime, prediction:float)->QueryStatus:
        pass
    


