import discord
import json
import asyncpg
from data.database import Database

class User_Data:
    def __init__(self, user: discord.User, guild: discord.Guild):
        self.user = user
        self.guild = guild
        self.vision = None
        self.is_premium = None

    async def get_db_columns(self):
        sql_get_query = "SELECT visions.vision, premium_users.id " \
                        "FROM users " \
                        "LEFT JOIN premium_users " \
                        "ON users.id = premium_users.user_id " \
                        "LEFT JOIN visions " \
                        "ON users.id = visions.user_id " \
                        f"WHERE users.id = {self.user.id} AND users.guild = {self.guild.id}"

        conn = await asyncpg.connect(Database.str_connection)
        result = await conn.fetch(sql_get_query)
        await conn.close()
        if result:
            self.vision = result[0][0]
            self.is_premium = result[0][1]
        return self

class Modifier:
    def __init__(self, user: discord.User, guild: discord.Guild):
        self.user = user
        self.guild = guild
        self.user_data: User_Data = None
        file_name = "global_modifiers/modifiers.json"
        with open(file_name, "r") as file:
            self.cfg = json.loads(file.read())
            cfg = self.cfg

        self.default_money_earn = cfg["default_money_earn"]
        self.default_exp_earn = cfg["default_exp_earn"]

        self.premium_money_earn = cfg["premium_money_earn"]
        self.premium_exp_earn = cfg["premium_exp_earn"]
        self.pattern = "_"

        self.exp_modifiers_dict = {}
        self.money_modifiers_dict = {}

    async def init(self):
        if self.user_data is None:
            self.user_data = User_Data(self.user, self.guild)
            await self.user_data.get_db_columns()

        if self.user_data.vision:
            self.vision_pattern = cutter(self.user_data.vision, self.pattern)

        await self.get_exp_modifier()
        await self.get_money_modifier()

    async def get_exp_modifier(self):

        result = self.default_exp_earn

        if self.user_data.is_premium is not None:
            result += self.premium_exp_earn
            self.exp_modifiers_dict["Premium"] = self.premium_exp_earn
        if self.user_data.vision:
            type_pattern = "exp"
            for key in self.cfg.keys():
                if self.vision_pattern in key:
                    if type_pattern in key:
                        result += self.cfg[key]
                        self.exp_modifiers_dict[f"God Vision ({self.vision_pattern})"] = self.cfg[key]

        self.exp_modifier = result
        round(self.exp_modifier, 2)

    async def get_money_modifier(self):

        result = self.default_money_earn

        if self.user_data.is_premium:
            result += self.premium_money_earn
            self.money_modifiers_dict["Premium"] = self.premium_money_earn
        if self.user_data.vision:
            type_pattern = "money"
            for key in self.cfg.keys():
                if self.vision_pattern in key:
                    if type_pattern in key:
                        result += self.cfg[key]
                        self.money_modifiers_dict[f"God Vision ({self.vision_pattern})"] = self.cfg[key]

        self.money_modifier = result


def cutter(row: str, pattern: str) -> str:
    for i in range(len(row)):
        if pattern is row[i]:
            output = row[:i].lower()
            return output

