import psycopg
import hashlib
import sys
sys.path.append("..")
from db_enums import DB_STATUS, AUTH_STATUS


async def get_user(api_key: str, connection:  psycopg.AsyncConnection) -> AUTH_STATUS:
    hashed_key = hashlib.md5(api_key.encode()).hexdigest()
    async with connection.cursor() as cursor:
        query = await cursor.execute("SELECT api_key FROM users WHERE api_key = %s", hashed_key)
        results = await query.fetchone()
    if len(results) >= 1:
        return AUTH_STATUS.GRANTED
    else:
        return AUTH_STATUS.DENIED

async def delete_user(username: str, password: str, connection:  psycopg.AsyncConnection) -> DB_STATUS:
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    try:
        async with connection.cursor() as cursor:
            query = await cursor.execute("SELECT * FROM users WHERE username = %s and pawword = %s",
                                     username, hashed_password)
            results = await query.fetchall()
            if results:
                query = await cursor.execute("DELETE FROM USERS WHERE username = %s AND password = %s", 
                                     username, hashed_password)
                results = await query.fetchall()
                return DB_STATUS.SUCCESS
            else:
                return DB_STATUS.DELETE_FAILURE
    except:
        return DB_STATUS.FAILURE



