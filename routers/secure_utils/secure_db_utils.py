import hashlib
from typing import Union
import os
import sqlite3
import re
from ..db_enums import DB_STATUS, AUTH_STATUS, PatternConstraints


async def get_user(api_key: str) -> AUTH_STATUS:
    hashed_key = hashlib.md5(api_key.encode()).hexdigest()
    db_name = os.getenv("DATABASE_PATH_NAME")
    assert db_name is not None
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        query = cursor.execute("SELECT api_key FROM users WHERE api_key = %s", hashed_key)
        results = query.fetchone()
    if len(results) >= 1:
        return AUTH_STATUS.GRANTED
    else:
        return AUTH_STATUS.DENIED

async def delete_db_user(username: str, password: str) -> DB_STATUS:
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    try:
        if re.fullmatch(PatternConstraints.USERNAME_PATTERN.value, username) is None:
            return DB_STATUS.USER_FAILURE
        if re.fullmatch(PatternConstraints.PASSWORD_PATTERN.value, password) is None:
            return DB_STATUS.USER_FAILURE

        db_name = os.getenv("DATABASE_PATH_NAME")
        assert db_name is not None
        with sqlite3.connect(db_name) as db:
            cursor = db.cursor()
            query = cursor.execute(
                f"SELECT * FROM users WHERE username = '{username}' and pawword = '{hashed_password}"
            )
            results = query.fetchall()
            if results:
                query = cursor.execute(
                    f"DELETE FROM USERS WHERE username = '{username}' AND password = '{hashed_password}'"
                )
                results = query.fetchall()
                db.commit()
                return DB_STATUS.SUCCESS
            else:
                return DB_STATUS.DELETE_FAILURE
    except:
        return DB_STATUS.FAILURE

def get_predictions_today(date: str) -> Union[dict, None]:
    try:
        db_name = os.getenv("DATABASE_PATH_NAME")
        assert db_name is not None
        with sqlite3.connect(db_name) as db:
            cursor = db.cursor()
            query = cursor.execute(
                f"SELECT game_id, inference_score from GAME_PREDICTIONS WHERE game_date = '{date}'"
            )

            game_scores = {
                row[0]: row[1] for row in query.fetchall()
            }
        return game_scores
    except:
        return None

def get_game_prediction_game_id(game_id: str) -> Union[float, None]:
    try:
        db_name = os.getenv("DATABASE_PATH_NAME")
        assert db_name is not None
        with sqlite3.connect(db_name) as db:
            cursor = db.cursor()
            query = cursor.execute(
                f"SELECT inference_score from GAME_PREDICTIONS WHERE game_id={game_id}"
            ).fetchone()
            if len(query) == 0:
                return -1.0
            else:
                return query[0]
    except:
        return None

