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
        self.left_border = None
        self.right_border = None
        if len(list_items) <= self.page_size:
            self.list_items_on_page = list_items
            self.left_border = 0
            self.right_border = len(list_items) - 1
        else:
            self.list_items_on_page = list_items[:self.page_size]
            self.left_border = 0
            self.right_border = len(self.list_items_on_page) - 1

    async def switch_page(self, is_move_forward: bool) -> bool:
        if is_move_forward:
            index_of_lst_element = self.right_border
            index_of_lst_element_on_page = index_of_lst_element + self.page_size
            if index_of_lst_element_on_page < len(self.const_list_items):
                self.list_items_on_page = self.const_list_items[index_of_lst_element + 1: index_of_lst_element_on_page]
                self.left_border = index_of_lst_element + 1
                self.right_border = index_of_lst_element_on_page - 1
                if index_of_lst_element_on_page + 1 < len(self.const_list_items):
                    return True
                return False
            else:
                self.list_items_on_page = self.const_list_items[index_of_lst_element + 1:]
                self.left_border = index_of_lst_element + 1
                self.right_border = len(self.const_list_items) - 1
                return False
        else:
            index_of_fst_element = self.left_border
            if index_of_fst_element > self.page_size:
                self.list_items_on_page = self.const_list_items[index_of_fst_element - self.page_size:index_of_fst_element]
                self.left_border = index_of_fst_element - self.page_size
                self.right_border = index_of_fst_element - 1
                return True
            else:
                self.list_items_on_page = self.const_list_items[:index_of_fst_element]
                self.left_border = 0
                self.right_border = index_of_fst_element - 1
                return False

    async def add_items_to_trade(self, items: []) -> bool:
        for item in items:
            self.items_to_trade.append(item)
            self.list_items.remove(item)
            self.right_border -= 1
            await self.update_current_page()
        return self.right_button_check()

    async def update_current_page(self):
        while len(self.list_items_on_page) < self.page_size:
            if self.right_border + 1 < len(self.list_items):
                self.right_border += 1
                self.list_items_on_page.append(self.list_items[self.right_border])
            else:
                break

    def right_button_check(self) -> bool:
        if self.right_border + 1 < len(self.list_items):
            return True
        return False

    def left_button_check(self) -> bool:
        if self.left_border == 0:
            return False
        return True

    async def is_page_empty(self) -> bool:
        if len(self.list_items_on_page) <= 0:
            await self.switch_page(False)
            return True
        else:
            return False




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





