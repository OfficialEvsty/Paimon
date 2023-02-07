
import os
import schedule
import shop_system.market
from bot import Bot
from commands.user_settings import *
import discord
import wavelink
import asyncio
import commands.user_settings
import commands.cmd_profile
import commands.cmd_main
import commands.cmd_inventory
import commands.cmd_money
import commands.cmd_hoyolab
import commands.cmd_waifu
import commands.cmd_admin
from typing import List
from commands.cmd_guild_settings import set_notifications_channel_id, set_transactions_channel_id
from discord.app_commands import describe, Choice
import music.custom_music
from item_system.inventory import Inventory
from item_system.generator import Generator
from waifu_system.waifu import Waifu
from waifu_system.harem import Harem
from rewarding.reward import Reward
from premium_system.premium import give_premium
from utilities.gif_creator.gif import FramesNotFound, IncorrectGifURL, MuchFramesInGif


bot = Bot()


async def items_autocomplete(
    interaction: discord.Interaction,
    current: int) -> List[discord.app_commands.Choice[int]]:
    items_by_type = Generator.all_items_by_type
    items = {items_by_type[index]['name']: items_by_type[index]['type'] for index in range(len(items_by_type))}
    return [
        discord.app_commands.Choice(name=item_name, value=item_type)
        for item_name, item_type in items.items()
    ]


@bot.tree.command(name="профиль", description="Показывает вашу карту профиля на сервере.")
async def app_show_card(interaction: discord.Interaction, user: discord.Member = None):
    await commands.cmd_profile.cmd_card(interaction, user)


@bot.tree.command(name="custom_embed", description="Создать сообщение вставку.")
async def app_custom_embed(interaction: discord.Interaction):
    await commands.cmd_main.create_custom_embed(interaction)


@bot.tree.command(name="инвентарь", description="Открыть инвентарь.")
async def inventory(interaction: discord.Interaction, is_private: bool = True):
    await commands.cmd_inventory.show_inventory(interaction, is_private)


@bot.tree.command(name="выдать_предметы", description="Положить предметы в инвентарь пользователю.")
@discord.app_commands.autocomplete(item=items_autocomplete)
@describe(item="Выберите предмет из списка.",
          quantity="Указать количество выбранных предметов.",
          user="Выбрать пользователя.")
async def app_add_items(interaction: discord.Interaction, item: int, quantity: int = 1, user: discord.User = None):
    items = [item] * quantity
    await shop_system.market.add_items(interaction, items, user)


@bot.tree.command(name="play", description="Paimon споёт ваш любимый трек.")
async def app_play(interaction: discord.Interaction, search: str):
    await music.custom_music.play(interaction, search)


@bot.tree.context_menu(name="профиль")
async def app_context_command(interaction: discord.Interaction, user: discord.User):
    return await commands.cmd_profile.cmd_card(interaction, user)


@bot.tree.context_menu(name="баланс")
async def app_context_balance(interaction: discord.Interaction, user: discord.User):
    return await commands.cmd_money.balance(interaction, user)


@bot.tree.command(name="награда")
async def app_reward(interaction: discord.Interaction, money: int = None, exp: int = None):
    reward = Reward(guild=interaction.guild, user=interaction.user, money=money, exp=exp)
    output = await reward.apply()
    return await interaction.response.send_message(output)


@bot.tree.command(name="баланс", description="Узнать свой баланс.")
async def app_balance(interaction: discord.Interaction):
    return await commands.cmd_money.balance(interaction)


@bot.tree.command(name="give", description="Передать игроку деньги")
async def app_give_money(interaction: discord.Interaction, user: discord.User, amount: int):
    await commands.cmd_money.give_money(interaction, user, amount)


@bot.tree.command(name="setup_bot_notifications", description="Эта команда устанавливает канал, в который бот будет присылать уведомления о прогрессе игроков.")
async def app_setup_notifications(interaction: discord.Interaction, is_disabled: bool = False):
    await set_notifications_channel_id(interaction, is_disabled)
    status = not is_disabled
    await interaction.response.send_message(f"Уведомления в канале `{interaction.channel}`: `{status}`", delete_after=10)


@bot.tree.command(name="setup_bot_transactions",
                  description="Установить канал, в который бот будет присылать транзакции между игроками.")
async def app_setup_transactions(interaction: discord.Interaction, is_disabled: bool = False):
    await set_transactions_channel_id(interaction, is_disabled)
    status = not is_disabled
    await interaction.response.send_message(f"Уведомления о транзакциях в канале `{interaction.channel}`: `{status}`",
                                            delete_after=10)


@bot.tree.command(name="premium", description="Выдать пользователю Premium статус. Разрешение:(Только разработчик)")
async def app_give_premium(interaction: discord.Interaction, user: discord.User, months: int = -1):
    if interaction.user.id == 285837413383929857:
        if months == -1:
            pass
        if months <= 12 and months > 0:
            await give_premium(user=user, months=months)


@bot.tree.command(name="hoyolab", description="Привязать свой аккаунт Discord к аккаунту Hoyolab.")
async def app_add_hoyolab(interaction: discord.Interaction, hoyolab_uid: int, hoyolab_token: str):
    await commands.cmd_hoyolab.add_hoyolab(interaction.user, hoyolab_uid, hoyolab_token)


@bot.tree.command(name="hoyo_stats", description="Показать статистику в Genshin Impact")
async def app_show_genshin_stats(interaction: discord.Interaction):
    await interaction.response.defer()
    await commands.cmd_hoyolab.get_hoyolab_stats(interaction)


@bot.tree.command(name="set_animated_profile", description="Установить анимированный профиль.")
async def app_set_animated_profile(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=False)
    try:
        await commands.cmd_profile.cmd_set_animated_profile(interaction, url)
    except IncorrectGifURL:
        await interaction.channel.send("Некорректная ссылка на изображение, расширение должно быть `.gif`.",
                                       delete_after=5)
    except MuchFramesInGif:
        await interaction.channel.send("В gif файле слишком много кадров, ограничение: не более 250.",
                                       delete_after=5)


@bot.tree.command(name="switch_premium_backgroung_mode", description="Поменять бэкграунд на премиум.")
async def turn_on_or_off_animated_background(interaction: discord.Interaction):
    await interaction.response.defer()
    is_enable = await commands.user_settings.turn_of_or_on_animated_background(interaction.user, interaction.guild)
    if is_enable:
        response = "включён"
    else:
        response = "отключён"
    await interaction.followup.send(f"Premium фон `{response}`")


@bot.tree.command(name="claim_waifu", description="Потребовать вайфу в гарем.")
async def claim_waifu(interaction: discord.Interaction, member: discord.Member):
    await commands.cmd_waifu.claim_waifu(interaction, member)


@bot.tree.command(name="show_harem", description="Показать гарем.")
async def show_harem(interaction: discord.Interaction):
    harem_mes = await commands.cmd_waifu.show_harem(interaction)
    await interaction.channel.send(harem_mes)


@bot.tree.command(name="upgrade_waifu", description="Повысить уровень вайфу.")
async def upgrade_waifu(interaction: discord.Interaction, member: discord.Member):
    await Waifu.upgrade_waifu_attribute(member)
    await Waifu.upgrade_waifu_cost(member, 200)
    await interaction.response.send_message(f"Уровень {member} повышен")


@bot.tree.command(name="waifu_work", description="Ваша вайфу принесет вам прибыль.")
async def waifu_work(interaction: discord.Interaction, member: discord.Member):
    harem = Harem(interaction.user, interaction.guild)
    await harem.get_info()
    await harem.do_working(member)
    await interaction.response.send_message(f"Вайфу {member} отправлена на работу.")


@bot.tree.command(name="take_gift", description="Принять подарок от вайфу.")
async def take_gift(interaction: discord.Interaction, member: discord.Member):
    harem = Harem(interaction.user, interaction.guild)
    await harem.get_info()
    waifu = harem.find_waifu(member)
    await waifu.gift()
    await interaction.response.send_message(f"Вайфу {member} подарила Вам подарок.")


@bot.tree.command(name="изменить_характеристики", description="Поменять характеристики вайфу")
@describe(member="Выбрать вайфу.",
          speed="Изменить характеристику скорости сбора подарка вайфу.",
          energy="Изменить характеристику энергии, вайфу будет быстрее востанавливаться.",
          profit="Изменить характеристику прибыли, которую вайфу приносит.",
          strength="Изменить характеристику усердности, ваша вайфу чаще дарит вам подарки.",
          luck="Изменить характеристику удачи, повышает вероятность найти в подарках что-то ценное.")
async def set_attrs(interaction: discord.Interaction,
                    member: discord.Member,
                    speed: int = None,
                    energy: int = None,
                    profit: int = None,
                    strength: int = None,
                    luck: int = None):
    is_complete = await commands.cmd_waifu.change_waifu_attrs(member, speed, energy, profit, strength, luck)
    if is_complete:
        await interaction.response.send_message(f"Характеристики Вайфу {member} были успешно изменены.", ephemeral=True,
                                                delete_after=5)
    else:
        await interaction.response.send_message(f"Введите значения в соответствующие характеристики.", ephemeral=True,
                                                delete_after=5)


@bot.tree.command(name="вайфу", description="Посмотреть вайфу.")
async def show_waifu_profile(interaction: discord.Interaction, member: discord.Member = None):
    await commands.cmd_waifu.show_profile(interaction, member=member)


@bot.tree.command(name="транзакции", description="Посмотреть транзакции пользователя за определенный период.")
@describe(member="Выбрать пользователя.",
          days="Транзакции, произошедшие за это количество дней.")
async def show_transactions(interaction: discord.Interaction, member: discord.Member, days: int = 7):
    await commands.cmd_admin.get_member_transactions(interaction=interaction, member=member, days=days)


@bot.tree.command(name="транзакция", description="Посмотреть транзакцию пользователя по её ID.")
@describe(transaction_id="ID транзакции.")
async def show_transaction(interaction: discord.Interaction, transaction_id: int):
    await commands.cmd_admin.get_transaction_by_id(interaction, transaction_id)

bot.startup()
os.environ['TOKEN'] = 'ODYwODA3ODc5NDE3NTI4MzIx.G8IL1T.IoPoLzzGIPpQr4UZNypmh8vR1JpEkcYe_-9CEk'
bot.run(os.getenv('TOKEN'))
