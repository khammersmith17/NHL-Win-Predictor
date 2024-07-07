import psycopg
import configparser

class DatabaseConnection:
    def __init__(self):
        self.dbname="kilianhammersmith"
        self.user="kilianhammersmith"
        self.password="K!l!an1998"
        self.port="5432"
        self.connection = None

    async def connect(self):
        self.connection = await psycopg.AsyncConnection.connect(f"""
                        dbname={self.dbname}
                        user={self.user}
                        password={self.password}
                        port={self.port}""")

db_instance = DatabaseConnection()
