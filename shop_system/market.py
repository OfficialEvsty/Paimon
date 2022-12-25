import discord
import discord.app_commands

import item_system.item_use.namecard
from item_system.generator import Generator
from item_system.inventory import Inventory


async def add_item(interaction: discord.Interaction, item_type: bytes, _user: discord.User = None):
    user = interaction.user
    if _user is not None:
        user = _user
    item = Generator.create_item(item_type)
    await Inventory.add_item(interaction, user, item)
    await interaction.response.send_message(f"{item.name} успешно добавлен в инвентарь {user}.", delete_after=5)
    print(f'{item} успешно добавлен в инвентарь {interaction.user}.')

