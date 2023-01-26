import discord
import asyncpg
import random
from gui.levelup import level_up_gui
from item_system.generator import Generator
from card_profile.profile import Profile
from data.database import Database
from gui.reward_gui import Reward_GUI
from commands.cmd_guild_settings import get_notifications_channel
from transaction_system.transaction import Transaction


class Reward:
    def __init__(self, guild: discord.Guild, user: discord.User, money: int = None, items: {} = None, exp: int = None):
        self.money = money
        self.items: {} = items
        self.exp = exp
        self.receiver = user
        self.guild = guild

    async def apply(self, is_notify: bool = True) -> str:
        notify_str = ""
        conn = await asyncpg.connect(Database.str_connection)
        if self.items is not None:
            notify_str += "Предметы:\n"
            items_list_to_insert_str = ""
            for slot in self.items.values():
                for item in slot:
                    items_list_to_insert_str += f"INSERT INTO items (guild, user_id, type) VALUES ({self.guild.id}, {self.receiver.id}, {item.type});"
                    notify_str += f"\t{item.name} добавлен в инвентарь {self.receiver}."

            items_add_to_user_query = "DO $$ " \
                                      "BEGIN " \
                                        f"{items_list_to_insert_str}" \
                                      f"END $$;"
            await conn.fetch(items_add_to_user_query)


        select_previous_queries_query = f"SELECT rank, xp, coins FROM users WHERE guild = {self.guild.id} AND id = {self.receiver.id}"
        result = await conn.fetch(select_previous_queries_query)

        if self.money is not None:
            notify_str += "Примогемы:\n"
            money_to_add_query = f"UPDATE users SET coins = {result[0][2] + self.money} WHERE guild = {self.guild.id} AND id = {self.receiver.id}"
            await conn.fetch(money_to_add_query)
            notify_str += f"\t{self.money} примогемов зачислено на счёт {self.receiver}."

        if self.exp is not None:
            notify_str += "Опыт:\n"
            _exp = result[0][1] + self.exp
            _rank = result[0][0]
            while _exp >= Profile.neededxp(_rank):
                _exp -= Profile.neededxp(_rank)
                _rank += 1
                await level_up_gui(self.guild, self.receiver, _rank)
                await level_up_reward(self.guild, self.receiver)

            xp_rank_to_add_query = f"UPDATE users SET xp = {_exp}, rank = {_rank} WHERE guild = {self.guild.id} AND id = {self.receiver.id}"
            await conn.fetch(xp_rank_to_add_query)
            notify_str += f"\t{self.receiver} получил {self.exp} опыта."
        await conn.close()

        if self.money is None and self.items is None:
            return notify_str
        if is_notify:
            await self.notify()
        return notify_str

    async def notify(self):
        reward_notification = Reward_GUI()
        buffer = reward_notification.draw(user=self.receiver, money=self.money, items=self.items)
        file = discord.File(fp=buffer, filename="reward_notification.png")
        notification_channel = await get_notifications_channel(self.guild)
        if notification_channel:
            await notification_channel.send(f"`{self.receiver}` получил награду", file=file)


async def level_up_reward(guild, user):
    min_money = 50
    max_money = 500
    min_count = 1
    max_count = 9
    money = random.randrange(min_money, max_money)
    count_wishes = random.randint(min_count, max_count)
    items = Generator.generate_random_items_by_group_type("wishing", count_wishes)
    reward = Reward(guild=guild, user=user, money=money, items=items)
    transaction_reward_for_level_up = Transaction(user, reason="Награда за повышение ранга.", money=money, received_items=items)
    await transaction_reward_for_level_up.send()
    await reward.apply()








