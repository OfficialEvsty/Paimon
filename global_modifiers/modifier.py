import discord
import json
import asyncpg
from data.database import Database

class User_Data:
    def __init__(self, member: discord.Member):
        self.member = member
        self.vision = None
        self.is_premium = None

    async def get_db_columns(self):
        sql_get_query = "SELECT vision, is_premium " \
                        "FROM users " \
                        "LEFT JOIN premium_users " \
                        "ON users.id = premium_users.user_id " \
                        f"WHERE users.id = {self.member.id} AND guild = {self.member.guild.id}"

        conn = await asyncpg.connect(Database.str_connection)
        result = await conn.fetch(sql_get_query)
        await conn.close()
        print(result)
        self.vision = result[0][0]
        self.is_premium = result[0][1]
        return self

class Modifier:
    def __init__(self, member: discord.Member):
        self.member = member
        self.user_data: User_Data = None
        file_name = "global_modifiers/modifiers.json"
        with open(file_name, "r") as file:
            self.cfg = json.loads(file.read())
            cfg = self.cfg

        self.default_money_earn = cfg["default_money_earn"]
        self.default_exp_earn = cfg["default_exp_earn"]

        self.premium_money_earn = cfg["premium_money_earn"]
        self.premium_exp_earn = cfg["premium_exp_earn"]

        self.exp_modifier = None
        self.money_modifier = None

    async def init(self):
        await self.get_exp_modifier()
        await self.get_money_modifier()

    async def get_exp_modifier(self):
        if self.user_data is None:
            self.user_data = User_Data(self.member)
            await self.user_data.get_db_columns()

        result = self.default_exp_earn

        if self.user_data.is_premium:
            result += self.premium_exp_earn

        #if self.user_data.vision is not None:
        self.exp_modifier = result



    async def get_money_modifier(self):
        if self.user_data is None:
            self.user_data = User_Data(self.member)
            await self.user_data.get_db_columns()

        result = self.default_money_earn

        self.money_modifier = result

