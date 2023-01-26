from discord import app_commands
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
from commands.cmd_guild_settings import set_notifications_channel_id, set_transactions_channel_id
import discord.app_commands
import music.custom_music
from item_system.inventory import Inventory
from item_system.generator import Generator
from waifu_system.waifu import Waifu
from waifu_system.harem import Harem
from rewarding.reward import Reward
from premium_system.premium import give_premium
from utilities.gif_creator.gif import FramesNotFound, IncorrectGifURL, MuchFramesInGif


bot = Bot()

class EmbedModal(discord.ui.Modal, title="Embed Constructor"):
    def __init__(self):
        super().__init__(
        )
        self.emTitle = discord.ui.TextInput(label="Embed Title", min_length=2, max_length=128, required=True, placeholder="Place your title here.")
        self.add_item(self.emTitle)

    async def on_submit(self, interaction: discord.Interaction):
        title = self.emTitle
        em = discord.Embed(title=title)
        return await interaction.response.send_message(embed=em)


@bot.tree.command(name="profile", description="Показывает вашу карту профиля на сервере.")
async def app_show_card(interaction: discord.Interaction, user: discord.Member = None):
    await commands.cmd_profile.cmd_card(interaction, user)


@bot.tree.command(name="custom_embed", description="Создать сообщение вставку.")
async def app_custom_embed(interaction: discord.Interaction):
    await commands.cmd_main.create_custom_embed(interaction)


@bot.tree.command(name="inventory", description="Открыть инвентарь.")
async def inventory(interaction: discord.Interaction, is_private: bool = True):
    await commands.cmd_inventory.show_inventory(interaction, is_private)


@bot.tree.command(name="give_item", description="Добавить предмет в свой инвентарь.")
async def app_add_item(interaction: discord.Interaction, item_type: int, user: discord.User = None):
    await shop_system.market.add_item(interaction, item_type, user)


@bot.tree.command(name="play", description="Paimon споёт ваш любимый трек.")
async def app_play(interaction: discord.Interaction, search: str):
    await music.custom_music.play(interaction, search)


@bot.tree.context_menu(name="profile")
async def app_context_command(interaction: discord.Interaction, user: discord.User):
    return await commands.cmd_profile.cmd_card(interaction, user)


@bot.tree.context_menu(name="balance")
async def app_context_balance(interaction: discord.Interaction, user: discord.User):
    return await commands.cmd_money.balance(interaction, user)


@bot.tree.command(name="reward")
async def app_reward(interaction: discord.Interaction, money: int = None, exp: int = None):
    reward = Reward(guild=interaction.guild, user=interaction.user, money=money, exp=exp)
    output = await reward.apply()
    return await interaction.response.send_message(output)


@bot.tree.command(name="balance", description="Узнать свой баланс.")
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


@take_gift()
async def set_attrs(interaction: discord.Interaction, member: discord.Member):
    await commands.cmd_waifu.change_waifu_attrs()
    await interaction.response.send_message(f"Вайфу {member} подарила Вам подарок.")

    set_attrs_command = discord.app_commands.Command(callback=set_attrs, name="Атрибуты", description="Установить атрибуты выбранной вайфу.")

    param = discord.app_commands.Parameter(command=set_attrs_command, parent=set_attrs_command)

bot.startup()
os.environ['TOKEN'] = 'ODYwODA3ODc5NDE3NTI4MzIx.G8IL1T.IoPoLzzGIPpQr4UZNypmh8vR1JpEkcYe_-9CEk'
bot.run(os.getenv('TOKEN'))
