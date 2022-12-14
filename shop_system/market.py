import discord
import discord.app_commands
from item_system.generator import Generator
from item_system.inventory import Inventory


async def add_item(interaction: discord.Interaction, item_type: bytes):
    item = Generator.create_item(item_type)
    await Inventory.add_item(interaction, item)
    print(f'{item} успешно добавлен в инвентарь {interaction.user}.')

