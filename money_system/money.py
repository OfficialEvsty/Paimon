import discord
import asyncpg
from data.database import Database


async def get_money_db(user: discord.User, guild: discord.Guild) -> int:
    conn = await asyncpg.connect(Database.str_connection)
    user_id = user.id
    guild = guild.id

    get_money_query = f"SELECT coins FROM users WHERE id = {user_id} AND guild = {guild}"
    result = await conn.fetch(get_money_query)
    await conn.close()
    current_money = result[0][0]
    return current_money


async def update_money_db(user: discord.User, guild: discord.Guild, delta: int) -> bool:
    conn = await asyncpg.connect(Database.str_connection)
    user_id = user.id
    guild = guild.id
    get_money_query = f"SELECT coins FROM users WHERE id = {user_id} AND guild = {guild}"
    result = await conn.fetch(get_money_query)
    if result:
        current_money = result[0][0]
        if delta < 0 and abs(delta) > current_money:
            await conn.close()
            return False

        updated_money = current_money + delta
        update_money_query = f"UPDATE users SET coins = {updated_money} WHERE id = {user_id} AND guild = {guild}"
        await conn.fetch(update_money_query)
    await conn.close()

    return True