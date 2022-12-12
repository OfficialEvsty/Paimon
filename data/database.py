import time
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
        print("Database opened successfully")
        on_create_table_users_query = 'CREATE TABLE IF NOT EXISTS users (' \
                                         'guild BIGINT NOT NULL, ' \
                                         'id BIGINT NOT NULL, ' \
                                         'rank INT NULL DEFAULT 1,' \
                                         ' xp INT NULL DEFAULT 0,' \
                                         'uid INT NULL, ' \
                                         'coins BIGINT NOT NULL DEFAULT 0, ' \
                                         'bio VARCHAR(100) NULL);'
        on_create_table_items_query ='CREATE TABLE IF NOT EXISTS items (' \
                                         'guild BIGINT NOT NULL, ' \
                                         'id SERIAL NOT NULL, ' \
                                         'user_id BIGINT NOT NULL, ' \
                                         'type SMALLINT NOT NULL, ' \
                                         'PRIMARY KEY(id)); '

        await self.conn.fetch(on_create_table_users_query)
        await self.conn.fetch(on_create_table_items_query)
        await self.conn.close()

    async def fetch(self, sql: str) -> list:

        pool = await asyncpg.create_pool(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        async with pool.acquire() as con:
            print(sql)
            result = await con.fetch(sql)
        await pool.close()

        return result

    async def filter(self, strict_pattern: str, dict_conditions: {}) -> str:
        filter_str = ""
        if len(dict_conditions) == 0:
            print("В словаре нету значений.")
        for (column, condition_val) in dict_conditions.items():
            if condition_val is str:
                filter_str += f"({column} = '{condition_val}')"
            else:
                filter_str += f"({column} = {condition_val}) "
            filter_str += f" {strict_pattern} "
        filter_str = filter_str[:(len(filter_str) - len(strict_pattern) - 2)]
        print(f"Фильтр: {filter_str}")
        return filter_str

    async def get_db(self, table: str, conditions_str: str, list_col_to_get: []):
        is_entry_exists = f'SELECT id FROM {table} WHERE {conditions_str}'
        if not await self.fetch(is_entry_exists):
            return []
        constructed_str = ""
        for i in range(len(list_col_to_get)):
            if i != len(list_col_to_get) - 1:
                constructed_str += f"{list_col_to_get[i]}, "
            else:
                constructed_str += f"{list_col_to_get[i]}"

        sql_query = f"SELECT {constructed_str} FROM {table} WHERE {conditions_str}"
        print(sql_query)
        result = await self.fetch(sql_query)
        print(result)
        if result:
            return result



    async def update_db(self, table: str, conditions_str: str, dict_col_val: {}):
        is_entry_exists = f'SELECT id FROM {table} WHERE {conditions_str}'
        str_to_insert = ""
        for (column, value) in dict_col_val.items():
            if column != 'id':
                if value is str:
                    str_to_insert += f"{column} = '{value}', "
                else:
                    str_to_insert += f"{column} = {value}, "
        if len(str_to_insert) > 2:
            str_to_insert = str_to_insert[:len(str_to_insert) - 2]
        sql_update = f'UPDATE {table} SET {str_to_insert} WHERE {conditions_str}'
        result = await self.fetch(is_entry_exists)
        if result:
            await self.fetch(sql_update)
            return True
        else:
            print("Запись невозможно обновить, так как её не существует.")
            return False

    async def set_db(self, table: str, conditions_str: str, dict_col_val: {}) -> bool:
        is_entry_exists = f'SELECT id FROM {table} WHERE {conditions_str}'

        columns_string = ""
        values_string = ""
        for (column, value) in dict_col_val.items():
            columns_string += f"{column}, "
            if value is str:
                values_string += f"'{value}', "
            else:
                values_string += f"{value}, "

        if len(columns_string) > 2:
            columns_string = columns_string[:len(columns_string)-2]
            values_string = values_string[:len(values_string) - 2]

        sql_insert = f'INSERT INTO {table} ({columns_string}) VALUES ({values_string})'

        result = await self.fetch(is_entry_exists)
        if result:
            print("Запись уже существует.")
            return False
        else:
            await self.fetch(sql_insert)
            return True

    async def delete(self, table: str, conditions_str: str):
        delete_query = f"DELETE FROM {table} WHERE {conditions_str}"
        self.fetch(delete_query)

    async def add_db(self, table: str, conditions_str: str, dict_col_val: {}) -> bool:
        columns_string = ""
        values_string = ""
        for (column, value) in dict_col_val.items():
            columns_string += f"{column}, "
            if value is str:
                values_string += f"'{value}', "
            else:
                values_string += f"{value}, "

        if len(columns_string) > 2:
            columns_string = columns_string[:len(columns_string)-2]
            values_string = values_string[:len(values_string) - 2]

        sql_insert = f'INSERT INTO {table} ({columns_string}) VALUES ({values_string})'

        await self.fetch(sql_insert)
        return True
