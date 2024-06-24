import numpy as np
from xgboost import DMatrix

def get_average(last_ten_games: dict) -> dict:
    for key in last_ten_games.keys():
        stat_arr = np.array(last_ten_games.get(key))
        last_ten_games.update({key:np.mean(stat_arr)})

        return last_ten_games

def get_matrix(array: np.array) -> DMatrix:
    return DMatrix(array)


