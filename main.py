from discord import app_commands

import schedule
import shop_system.market
from bot import Bot
from commands.user_info import *
import discord
import wavelink
import asyncio
import commands.user_info
import commands.cmd_profile
import commands.cmd_main
import commands.cmd_inventory
import commands.cmd_money
from commands.cmd_guild_settings import set_notifications_channel_id, set_transactions_channel_id
import discord.app_commands
import music.custom_music
from item_system.inventory import Inventory
from item_system.generator import Generator
from rewarding.reward import Reward
from premium_system.premium import check_premium



if __name__ == "__main__":
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


    @bot.tree.command(name="get_uid", description="Увидеть свой UID на сервере.")
    async def app_get_uid(interaction: discord.Interaction):
        await commands.user_info.cmd_get_uid(interaction)


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
    async def app_give_premium(interaction: discord.Interaction, user_id: int, months: int = -1):
        if months == -1:
            pass
        if months <= 12 and months > 0:
            pass

    bot.startup()
    bot.run(bot.cfg.token)

    pass