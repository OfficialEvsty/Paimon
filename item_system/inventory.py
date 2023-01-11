import discord
import asyncpg
from bot import Bot
from data.database import Database


class Inventory:
    def __init__(self, list_items: []):
        self.const_list_items = list_items
        self.list_items = list_items
        self.page_size = 10
        self.items_to_trade = []

    @classmethod
    async def get_inventory(cls, interaction: discord.Interaction):
        user_called_id = interaction.user.id
        condition_pattern = "AND"
        conditions_dict = {"user_id": user_called_id, "guild": interaction.guild.id}
        list_column = ["id", "type"]
        records_item = await Bot.db.get_db(table="items",
                                           conditions_str=await Bot.db.filter(condition_pattern, conditions_dict),
                                           list_col_to_get=list_column)
        return records_item

    @classmethod
    async def add_item(cls, interaction: discord.Interaction, user: discord.User, item):
        user = user
        user_id = user.id
        guild_id = interaction.guild.id

        table = "items"
        conditions_dict = {"user_id" : user_id, "guild" : guild_id}
        condition_pattern = "AND"
        dict_container = {"user_id" : user_id, "guild" : guild_id, "type" : item.type}
        await Bot.db.add_db(table, await Bot.db.filter(condition_pattern, conditions_dict), dict_container)

    @classmethod
    async def remove_item(cls, interaction: discord.Interaction, item_id : int):
        """

        :rtype: object
        """
        table = "items"
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        condition_pattern = "AND"
        conditions_dict = {"user_id" : user_id, "guild" : guild_id, "id" : item_id}
        await Bot.db.delete(table, await Bot.db.filter(condition_pattern, conditions_dict))

    @classmethod
    async def withdraw_items_from_inventory(cls, guild: discord.Guild, items: []):
        guild = guild.id
        conn = await asyncpg.connect(Database.str_connection)
        for item in items:
            withdraw_from_inventory_query = f"UPDATE items SET user_id = {guild} WHERE id = {item.id}"
            await conn.fetch(withdraw_from_inventory_query)
        await conn.close()

    @classmethod
    async def draw_items_in_inventory(cls, user: discord.User, items: []):

        conn = await asyncpg.connect(Database.str_connection)
        for item in items:
            draw_in_inventory_query = f"UPDATE items SET user_id = {user.id} WHERE id = {item.id}"
            await conn.fetch(draw_in_inventory_query)
        await conn.close()





