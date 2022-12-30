import random
import time
import discord

from data.database import Database
from card_profile.profile import Profile
from random import randint
from rewarding.reward import level_up_reward, Reward
from gui.levelup import level_up_gui
from global_modifiers.modifier import Modifier
import asyncpg
import asyncio


class Leveling:

    def __init__(self, min_xp, max_xp, time):
        self.min_xp_message = min_xp
        self.max_xp_message = max_xp
        self.ignoring_time = time
        self.vc_timer_min = 5
        self.max_xp_vc = 50
        self.min_xp_vc = 10
        self.max_money_vc = 40
        self.min_money_vc = 25
        self.loop = asyncio.get_event_loop()

    ignoring_user_list = []
    users_in_vc = []
    timers_for_users_dict = {}

    async def add_message_xp(self, guild, user: discord.User) -> None:
        if guild is None:
            return
        guild_id = guild.id
        user_id = user.id
        if user_id not in self.ignoring_user_list:

            pool = await asyncpg.create_pool(Database.str_connection)
            async with pool.acquire() as conn:

                if not await conn.fetch(f"SELECT id FROM users WHERE id = {user_id} AND guild = {guild_id}"):
                    await conn.fetch(f"INSERT INTO users (guild, id, rank) VALUES ({guild_id}, {user_id}, 1)")

                result = await conn.fetch(f"SELECT xp, rank FROM users WHERE id = {user_id} AND guild = {guild_id}")
                if result:
                    current_xp = result[0][0]
                    current_xp += randint(self.min_xp_message, self.max_xp_message)
                    current_rank = result[0][1]
                    if current_xp >= Profile.neededxp(current_rank):
                        current_rank += 1
                        await level_up_gui(guild, user, current_rank)
                        await level_up_reward(guild, user)
                        current_xp = 0
                    await conn.fetch(f"UPDATE users SET xp = {current_xp}, rank = {current_rank} WHERE id = {user_id} AND guild = {guild_id}")
            await pool.close()

    async def add_voice_xp(self, guild, user: discord.User):
        pass

    async def timer(self, member: discord.Member, minutes: int):
        while True:
            for min in range(minutes, 0, -1):
                print(f"{min} минут осталось.")
                await asyncio.sleep(60)
            await self.vc_rewarding_for_timeout(member)
            print(f"Таймер окончен.")

    async def check_vc_for_user(self):


        for member in self.users_in_vc:
            if member in self.timers_for_users_dict.keys():
                continue
            else:
                self.timers_for_users_dict[member] = asyncio.create_task(self.timer(member, self.vc_timer_min))
                print(f"{member.name} успешно добавлен в список отслеживаемых пользователей в голосовом канале.")


        list_dicts_for_delete = []
        for (member, coro) in self.timers_for_users_dict.items():
            if member in self.users_in_vc:
                continue
            else:
                self.timers_for_users_dict[member].cancel()
                list_dicts_for_delete.append(member)

        for member_key in list_dicts_for_delete:
            print(f"{member_key.name} успешно удален из списка отслеживаемых пользователей в голосовом канале.")
            if member_key in self.timers_for_users_dict.keys():
                self.timers_for_users_dict.pop(member_key)
        print(self.timers_for_users_dict)


    async def vc_rewarding_for_timeout(self, member: discord.Member):
        xp = random.randrange(self.min_xp_vc, self.max_xp_vc)
        money = random.randrange(self.min_money_vc, self.max_money_vc)



        guild = member.guild
        reward = Reward(guild, member, money=money, exp=xp)
        await reward.apply()
        print("Получил награду")




