
import time
from data.database import Database
from card_profile.profile import Profile
from random import randint
from rewarding.reward import level_up_reward
from gui.levelup import level_up_gui
import asyncpg


class Leveling:

    def __init__(self, min_xp, max_xp, time):
        self.min_xp_message = min_xp
        self.max_xp_message = max_xp
        self.ignoring_time = time

    ignoring_user_list = []


    async def add_message_xp(self, guild, user: int) -> None:
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


