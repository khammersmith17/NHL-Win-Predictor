from enum import Enum
import pyscopg
import hashlib
import secrets
from typing import Union


class PatternConstraints(Enum):
    PASSWORD_PATTERN = "^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}"
    USERNAME_PATTERN = "^[0-9A-Za-z]{6,16}"


async def write_user(username: str, password: str, connection: pyscopg.Connection.cursor) -> tuple[int, Union[str, None]]:
    try:
        password = hashlib.md5(password.encode()).hexdigest()
        api_key = secrets.token_urlsafe(32)
        hashed_api_key = hashlib.md5(api_key.encode()).hexdigest()
        async with connection.cursor() as cursor: 
            await cursor.execute(
                "INSERT INTO users  (id, username, password, api_key) VALUES (%s, %s, %s. %s)",
                (id, username, password, hashed_api_key))
            await cursor.commit()

        return DB_STATUS.SUCCESS.value, api_key

    except:
        return DB_STATUS.FAILURE.value, None

