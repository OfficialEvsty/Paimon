import discord
import asyncpg
from item_system.inventory import Inventory
from data.database import Database


usage_functions_dict = {}


def add_item_use(func_usage):
    usage_functions_dict[func_usage.__name__] = func_usage

    def on_use(interaction: discord.Interaction, items):
        func_usage(interaction, items)

    return on_use


# Decorator
def usable(func_usage):
    async def on_use(interaction: discord.Interaction, items: [] = None):
        item = items[0]
        if item.usable:
            await func_usage(interaction, items)
            if item.consumable:
                print(f"`{len(items)}`шт `{item.name}` успешно использовано и потрачено.")
                await Inventory.remove_items(items)
        else:
            print("Предмет не является используемым.")

    return on_use
