import time

import psycopg2
import asyncpg


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.name = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.str_connection = f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    #Должна существовать бд Paimon

    async def connect(self) -> None:
        self.conn = await asyncpg.connect(dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        on_create_tables_query = 'CREATE TABLE IF NOT EXISTS users (id BIGINT NOT NULL, rank INT NULL, xp INT NULL,' \
                                     'uid INT NULL, coins BIGINT NULL, bio VARCHAR(60) NULL)'
        await self.conn.fetch(on_create_tables_query)
        await self.conn.close()
    async def fetch(self, sql: str) -> list:

        pool = await asyncpg.create_pool(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        async with pool.acquire() as con:
            print(sql)
            result = await con.fetch(sql)
        await pool.close()

        return result

        """self.conn = await asyncpg.connect(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        print(sql)
        return await self.conn.fetch(sql)"""

