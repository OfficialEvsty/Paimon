from data.database import Database
from discord import Member
import asyncpg

attr_dict = {
        0: "energy",
        1: "speed",
        2: "profit",
        3: "luck",
        4: "strength"
    }


async def upgrade_attribute(member: Member, index: int, level_count: int = 1):
    attr_name = attr_dict[index]
    conn = await asyncpg.connect(Database.str_connection)
    increment_attribute_query = f"UPDATE waifu_stats SET {attr_name} = (SELECT {attr_name} FROM waifu_stats " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}) + {level_count} " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(increment_attribute_query)
    await conn.close()


async def update_cost_of_waifu(member: Member, level_cost: int):
    conn = await asyncpg.connect(Database.str_connection)
    update_cost_of_waifu_query = f"UPDATE waifu_stats SET cost = (SELECT cost FROM waifu_stats " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}) + {level_cost} " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(update_cost_of_waifu_query)
    await conn.close()


async def update_working_status(member: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)
    update_working_status_query = f"UPDATE waifu_stats SET working_status = {status} " \
                                  f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(update_working_status_query)
    await conn.close()


async def update_resting_status(member: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)
    update_resting_status_query = f"UPDATE waifu_stats SET resting_status = {status} " \
                                  f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(update_resting_status_query)
    await conn.close()