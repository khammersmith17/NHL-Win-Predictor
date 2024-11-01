import sqlite3
import hashlib
import secrets
from typing import Union
from ..db_enums import DB_STATUS
import os


async def write_user(username: str, password: str) -> tuple[int, Union[str, None]]:
    try:
        password = hashlib.md5(password.encode()).hexdigest()
        api_key = secrets.token_urlsafe(32)
        hashed_api_key = hashlib.md5(api_key.encode()).hexdigest()
        db_name = os.getenv("DATABASE_NAME")
        assert db_name is not None
        with sqlite3.connect(db_name) as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users  (id, username, password, api_key) VALUES (%s, %s, %s. %s)",
                (id, username, password, hashed_api_key))
            db.commit()

        return DB_STATUS.SUCCESS.value, api_key

    except:
        return DB_STATUS.FAILURE.value, None

