from card_profile.profile import Profile
from random import randint
import bot
import asyncpg


class Leveling:

    def __init__(self, min_xp, max_xp, time):
        self.min_xp_message = min_xp
        self.max_xp_message = max_xp
        self.ignoring_time = time

    ignoring_user_list = []


    async def add_message_xp(self, guild_id, user_id: int) -> None:
        if user_id not in self.ignoring_user_list:
            pool = await asyncpg.create_pool(bot.Bot.db.str_connection)
            async with pool.acquire() as conn:

                if not await conn.fetch(f"SELECT id FROM users WHERE id = {user_id} AND guild = {guild_id}"):
                    await conn.fetch(f"INSERT INTO users (guild, id, xp, rank) VALUES ({guild_id}, {user_id}, 0, 0)")
                result = await conn.fetch(f"SELECT xp, rank FROM users WHERE id = {user_id} AND guild = {guild_id}")
                if result[0][0] == None or result[0][1] == None:
                    await conn.fetch(f'UPDATE users SET xp=0, rank=0 WHERE id = {user_id} AND guild = {guild_id}')

                result = await conn.fetch(f"SELECT xp, rank FROM users WHERE id = {user_id} AND guild = {guild_id}")
                if result:
                    current_xp = result[0][0]
                    print(current_xp)
                    print(randint(self.min_xp_message, self.max_xp_message))
                    current_xp += randint(self.min_xp_message, self.max_xp_message)
                    current_rank = result[0][1]
                    if current_xp >= Profile.neededxp(current_rank):
                        current_rank += 1
                        current_xp = 0
                    await conn.fetch(f"UPDATE users SET xp = {current_xp}, rank = {current_rank} WHERE id = {user_id} AND guild = {guild_id}")
            await pool.close()
