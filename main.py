from discord import app_commands

import shop_system.market
from bot import Bot
from commands.user_info import *
import discord
import commands.user_info
import commands.cmd_profile
import commands.cmd_main
import commands.cmd_inventory
import discord.app_commands
from item_system.inventory import Inventory
from item_system.generator import Generator



if __name__ == "__main__":
    bot = Bot()








    @bot.tree.command(name="animedolbayeb", description="his greetings message welcomes u!")
    async def self(interaction: discord.Interaction, name: str):
        await commands.cmd_main.show_tips(interaction)


    @bot.tree.command(name="profile", description="Показывает вашу карту профиля на сервере.")
    async def app_show_card(interaction: discord.Interaction, user: discord.Member = None):
        await commands.cmd_profile.cmd_card(interaction, user)


    @bot.tree.command(name="set_uid", description="Зарегистрировать свой UID в дискорде. Это поможет легче взаимодейстовать с Паймон.")
    async def app_set_uid(interaction: discord.Interaction, uid: int):
        await commands.user_info.cmd_set_uid(interaction, uid)


    @bot.tree.command(name="get_uid", description="Увидеть свой UID на сервере.")
    async def app_get_uid(interaction: discord.Interaction):
        await commands.user_info.cmd_get_uid(interaction)


    @bot.tree.command(name="bio", description="Добавить информацию о себе, чтобы вас смогли узнать получше.")
    async def app_bio(interaction: discord.Interaction, text: str):
        await commands.user_info.cmd_bio(interaction, text)


    @bot.tree.command(name="custom_embed", description="Создать сообщение вставку.")
    async def app_custom_embed(interaction: discord.Interaction, title: str = None, description: str = None, color: int = None, image_url: str = None,
                              tumbnail: str = None):
        await commands.cmd_main.create_custom_embed(interaction, title, description, color, image_url, tumbnail)

    @bot.tree.command(name="inventory", description="Открыть инвентарь.")
    async def inventory(interaction: discord.Interaction):
        await commands.cmd_inventory.show_inventory(interaction)

    @bot.tree.command(name="get_item", description="Добавить предмет в свой инвентарь.")
    async def app_add_item(interaction: discord.Interaction, item_type: int):
        await shop_system.market.add_item(interaction, item_type)

    bot.startup()
    bot.run(bot.cfg.token)
    pass