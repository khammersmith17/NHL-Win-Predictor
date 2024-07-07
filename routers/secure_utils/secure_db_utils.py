import psycopg
from enum import Enum
import hashlib


class AUTH_STATUS(Enum):
    GRANTED = 1
    DENIED = 0

async def get_user(api_key: str, connection:  pyscopg.AsyncConnection) -> AUTH_STATUS:
    hashed_key =  hashlib.md5(api_key.encode()).hexdigest()
    async with connection.cursor() as cursor:
    query = await cursor.execute("SELECT api_key FROM users WHERE api_key = %s", hashed_key)
    results = await query.fetchone()
    if len(results) >= 1:
        return AUTH_STATUS.GRANTED
    else:
        return AUTH_STATUS.DENIED


