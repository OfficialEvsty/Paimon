import time
import asyncpg


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.name = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    str_connection = ""

    #Должна существовать бд Paimon

    async def connect(self) -> None:
        Database.str_connection = f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        self.conn = await asyncpg.connect(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}")

        # is_db_paimon_exists = "SELECT * FROM pg_catalog.pg_database"
        # exists = await self.conn.fetch(is_db_paimon_exists)
        try:
            await self.conn.execute("CREATE DATABASE paimon")
        except:
            print("Database already created.")

        await self.conn.close()

        self.conn = await asyncpg.connect(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")

        print("Database opened successfully")
        on_create_table_users_query = 'CREATE TABLE IF NOT EXISTS users (' \
                                         'guild BIGINT NOT NULL, ' \
                                         'id BIGINT NOT NULL, ' \
                                         'rank INT NULL DEFAULT 1,' \
                                         'xp INT NULL DEFAULT 0,' \
                                         'uid INT NULL, ' \
                                         "namecard VARCHAR(200) NULL DEFAULT 'Default', " \
                                         "vision VARCHAR(50) NULL, " \
                                         'coins BIGINT NOT NULL DEFAULT 0, ' \
                                         'bio VARCHAR(100) NULL);'
        on_create_table_items_query ='CREATE TABLE IF NOT EXISTS items (' \
                                         'guild BIGINT NOT NULL, ' \
                                         'id SERIAL NOT NULL, ' \
                                         'user_id BIGINT NOT NULL, ' \
                                         'type SMALLINT NOT NULL, ' \
                                         'PRIMARY KEY(id)); '
        on_create_table_namecards_query ='CREATE TABLE IF NOT EXISTS namecards (' \
                                         'id SERIAL NOT NULL, ' \
                                         'user_id BIGINT NOT NULL, ' \
                                         'namecard VARCHAR(100) NOT NULL, ' \
                                         'PRIMARY KEY(id));'
        on_create_table_visions_query = 'CREATE TABLE IF NOT EXISTS visions (' \
                                        'id SERIAL NOT NULL, ' \
                                        'user_id BIGINT NOT NULL, ' \
                                        'guild BIGINT NOT NULL, ' \
                                        'vision VARCHAR(50) NOT NULL, ' \
                                        'item_id BIGINT NOT NULL, ' \
                                        'PRIMARY KEY(id),' \
                                        'FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE);'

        on_create_table_guilds_guery = 'CREATE TABLE IF NOT EXISTS guilds (' \
                                       'id BIGINT NOT NULL, ' \
                                       'users_notify_channel_id BIGINT NULL, ' \
                                       'transactions_channel_id BIGINT NULL, ' \
                                       'PRIMARY KEY(id));'

        on_create_table_premium_users_query = 'CREATE TABLE IF NOT EXISTS premium_users (' \
                                              'id SERIAL NOT NULL, ' \
                                              'user_id BIGINT NOT NULL, ' \
                                              'until_date DATE NOT NULL, ' \
                                              'PRIMARY KEY(id));' \

        on_create_table_hoyolab_data_query = 'CREATE TABLE IF NOT EXISTS hoyolab_data (' \
                                             'id SERIAL NOT NULL, ' \
                                             'user_id BIGINT NOT NULL, ' \
                                             'ltuid BIGINT NOT NULL, ' \
                                             'ltoken VARCHAR(40) NOT NULL, ' \
                                             'PRIMARY KEY(id));'

        on_create_table_files_query = 'CREATE TABLE IF NOT EXISTS files (' \
                                      'id SERIAL NOT NULL, ' \
                                      'user_id BIGINT NOT NULL,' \
                                      'guild BIGINT NOT NULL, ' \
                                      'gif BYTEA NOT NULL, ' \
                                      'PRIMARY KEY(id));'

        on_create_table_user_settings_query = 'CREATE TABLE IF NOT EXISTS user_settings (' \
                                              'id SERIAL NOT NULL, ' \
                                              'user_id BIGINT NOT NULL, ' \
                                              'guild BIGINT NOT NULL, ' \
                                              'is_premium_background BOOLEAN DEFAULT FALSE, ' \
                                              'PRIMARY KEY(id));'

        on_create_table_waifu_stats_query = 'CREATE TABLE IF NOT EXISTS waifu_stats (' \
                                              'id SERIAL NOT NULL, ' \
                                              'user_id BIGINT NOT NULL, ' \
                                              'guild BIGINT NOT NULL, ' \
                                              'energy BIGINT NOT NULL DEFAULT 0, ' \
                                              'speed BIGINT NOT NULL DEFAULT 0, ' \
                                              'profit BIGINT NOT NULL DEFAULT 0, ' \
                                              'luck BIGINT NOT NULL DEFAULT 0, ' \
                                              'strength BIGINT NOT NULL DEFAULT 0, ' \
                                              'cost BIGINT NOT NULL DEFAULT 100, ' \
                                              'lover BIGINT NULL, ' \
                                              'working_status BOOLEAN DEFAULT False, ' \
                                              'resting_status BOOLEAN DEFAULT False, ' \
                                              'gift_status BOOLEAN DEFAULT False, ' \
                                              'PRIMARY KEY(id));'
        # It's not a waifus in correct of meaning of this word, this multiple of waifu.
        on_create_table_waifus_query = 'CREATE TABLE IF NOT EXISTS waifus (' \
                                       'id SERIAL NOT NULL, ' \
                                       'guild BIGINT NOT NULL, ' \
                                       'owner BIGINT NOT NULL, ' \
                                       'waifu BIGINT NOT NULL, ' \
                                       'PRIMARY KEY(id));'

        on_create_function_on_update_item_owner = 'CREATE OR REPLACE FUNCTION on_switch_vision_owner() ' \
                                          'RETURNS trigger AS $tab$ ' \
                                          'BEGIN ' \
                                                f'IF EXISTS (' \
                                                f'SELECT * FROM visions WHERE item_id = OLD.id) THEN ' \
                                                    f'DELETE FROM visions WHERE item_id = OLD.id;' \
                                                f'END IF;' \
                                                f'RETURN NEW;' \
                                          f'END; ' \
                                          f'$tab$ LANGUAGE plpgsql'

        on_create_trigger_when_item_owner_changes = 'CREATE OR REPLACE TRIGGER owner_changed_trig ' \
                                                    'AFTER UPDATE OF user_id ON items ' \
                                                    'FOR EACH ROW EXECUTE PROCEDURE on_switch_vision_owner();'

        await self.conn.fetch(on_create_table_user_settings_query)
        await self.conn.fetch(on_create_table_namecards_query)
        await self.conn.fetch(on_create_table_users_query)
        await self.conn.fetch(on_create_table_items_query)
        await self.conn.fetch(on_create_table_guilds_guery)
        await self.conn.fetch(on_create_table_premium_users_query)
        await self.conn.fetch(on_create_table_hoyolab_data_query)
        await self.conn.fetch(on_create_table_visions_query)
        await self.conn.fetch(on_create_table_files_query)
        await self.conn.fetch(on_create_table_waifu_stats_query)
        await self.conn.fetch(on_create_table_waifus_query)

        await self.conn.fetch(on_create_function_on_update_item_owner)

        await self.conn.fetch(on_create_trigger_when_item_owner_changes)

        await self.conn.close()

    async def fetch(self, sql: str) -> list:

        pool = await asyncpg.create_pool(
            dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        async with pool.acquire() as con:
            result = await con.fetch(sql)
        await pool.close()

        return result

    async def filter(self, strict_pattern: str, dict_conditions: {}) -> str:
        filter_str = ""
        for (column, condition_val) in dict_conditions.items():
            if condition_val is str:
                filter_str += f"({column} = '{condition_val}')"
            else:
                filter_str += f"({column} = {condition_val}) "
            filter_str += f" {strict_pattern} "
        filter_str = filter_str[:(len(filter_str) - len(strict_pattern) - 2)]
        return filter_str

    async def get_db(self, table: str, conditions_str: str, list_col_to_get: []):
        conn = await asyncpg.connect(Database.str_connection)
        is_entry_exists = f'SELECT id FROM {table} WHERE {conditions_str}'
        if not await conn.fetch(is_entry_exists):
            return []
        constructed_str = ""
        for i in range(len(list_col_to_get)):
            if i != len(list_col_to_get) - 1:
                constructed_str += f"{list_col_to_get[i]}, "
            else:
                constructed_str += f"{list_col_to_get[i]}"

        sql_query = f"SELECT {constructed_str} FROM {table} WHERE {conditions_str}"
        result = await conn.fetch(sql_query)
        if result:
            return result
        await conn.close()



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
        await self.fetch(delete_query)

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
