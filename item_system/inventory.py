import discord
from bot import Bot

from item_system.item import Item

class Inventory:
    def __init__(self, list_items: []):
        self.list_items = list_items

    def show(self):
        output = ""
        for item in self.list_items:
            output += (f"Id: {item.id}\n"
                         f"Name: {item.name}\n"
                         f"Type: {item.type}\n"
                         f"Usable: {item.usable}\n"
                         f"Stackable: {item.stackable}\n"
                         f"Consumable: {item.consumable}\n"
                         f"Value: {item.value}\n"
                         f"Description: {item.description}\n\n")
        return output

    @classmethod
    async def add_item(cls, interaction: discord.Interaction, item : Item):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        table = "items"
        conditions_dict = {"user_id" : user_id, "guild" : guild_id}
        condition_pattern = "AND"
        dict_container = {"user_id" : user_id, "guild" : guild_id, "type" : item.type}
        await Bot.db.add_db(table, await Bot.db.filter(condition_pattern, conditions_dict), dict_container)

    @classmethod
    async def remove_item(cls, interaction: discord.Interaction, item_id : int):
        table = "items"
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        condition_pattern = "AND"
        conditions_dict = {"user_id" : user_id, "guild" : guild_id, "id" : item_id}
        await Bot.db.delete(table, await Bot.db.filter(condition_pattern, conditions_dict))


