from data.database import Database
from discord import Member, Guild
import asyncpg

attr_dict = {
        0: "energy",
        1: "speed",
        2: "profit",
        3: "luck",
        4: "strength"
    }


async def insert_waifu(member: Member, conn: asyncpg.Connection):
    insert_waifu_sql = "DO $$ " \
                                 "BEGIN " \
                                    "IF NOT EXISTS(" \
                                    "SELECT * FROM waifus " \
                                    f"WHERE guild = {member.guild.id} AND waifu = {member.id}) THEN " \
                                        f"INSERT INTO waifus (guild, waifu) " \
                                        f"VALUES ({member.guild.id}, {member.id}); " \
                                        f"INSERT INTO waifu_stats (guild, user_id) " \
                                        f"VALUES ({member.guild.id}, {member.id}); " \
                                 f"END IF;" \
                                 f"END $$;"
    await conn.fetch(insert_waifu_sql)


async def change_waifu_attrs(member: Member, speed: int = None, energy: int = None, profit: int = None,
                             strength: int = None, luck: int = None):
    conn = await asyncpg.connect(Database.str_connection)
    await insert_waifu(member, conn)
    update_attrs_beginning_query = f"UPDATE waifu_stats SET "
    update_attrs_query = ""
    if speed:
        update_attrs_query += f"speed = {speed} "
    if energy:
        update_attrs_query += f"energy = {energy} "
    if profit:
        update_attrs_query += f"profit = {profit} "
    if strength:
        update_attrs_query += f"strength = {strength} "
    if luck:
        update_attrs_query += f"luck = {luck} "

    update_attrs_ending_query = f"WHERE guild = {member.guild.id} AND waifu = {member.id};"
    result_query = update_attrs_beginning_query + update_attrs_query + update_attrs_ending_query
    await conn.fetch(result_query)


async def delete_waifu(waifu_id: int, guild: Guild):
    conn = await asyncpg.connect(Database.str_connection)
    delete_waifu_query = f"DELETE FROM waifus WHERE guild = {guild.id} AND waifu = {waifu_id}"
    await conn.fetch(delete_waifu_query)
    await delete_waifu_stats(waifu_id, guild)
    await conn.close()


async def delete_waifu_stats(waifu_id: int, guild: Guild):
    conn = await asyncpg.connect(Database.str_connection)
    delete_waifu_stats_query = f"DELETE FROM waifu_stats WHERE guild = {guild.id} AND user_id = {waifu_id}"
    await conn.fetch(delete_waifu_stats_query)
    await conn.close()


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


async def update_gift_status(member: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)
    update_gift_status_query = f"UPDATE waifu_stats SET gift_status = {status} " \
                                  f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(update_gift_status_query)
    await conn.close()
