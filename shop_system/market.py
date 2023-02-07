import discord
import discord.app_commands

import item_system.item_use.namecard
from item_system.generator import Generator
from item_system.inventory import Inventory


async def add_items(interaction: discord.Interaction, items_id: [], _user: discord.User = None):
    user = interaction.user
    if _user is not None:
        user = _user
    await Inventory.add_items(interaction, user, items_id)
    await interaction.response.send_message(f"Предметы успешно добавлены в инвентарь {user}.", delete_after=5)

