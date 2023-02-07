from data.database import Database
from discord import Member, Guild
from typing import List
from utilities.randomizer import Randomizer
from waifu_system.waifu_stats import WaifuStats
from waifu_system.exceptions import WaifuNotFound, InteractingNotOwner, OwnerDoesNotExist
import asyncpg
import discord

attr_dict = {
        0: "energy",
        1: "speed",
        2: "profit",
        3: "luck",
        4: "strength"
    }


def is_owner_valid(owner_id: int, interacting_id: int):
    if owner_id == interacting_id:
        return
    raise InteractingNotOwner(owner_id, interacting_id)


async def check_owner(interacting: Member, waifu: Member, conn: asyncpg.Connection):
    owner_id = await get_owner(waifu, conn)
    if owner_id:
        is_owner_valid(owner_id, interacting.id)
    else:
        raise OwnerDoesNotExist(waifu)
# Select queries


async def get_owner(waifu: Member, conn: asyncpg.Connection) -> int:
    get_owner_query = f"SELECT owner FROM waifus WHERE guild = {waifu.guild.id} AND waifu = {waifu.id};"
    result = await conn.fetch(get_owner_query)
    owner_id = result[0][0]
    return owner_id


# as Waifu presence.
async def if_exists_get_else_insert_waifu_owner(owner: Member, conn: asyncpg.Connection) -> tuple:
    get_owner_and_waifu_ids_query = f"SELECT waifu, owner FROM waifus WHERE waifu = {owner.id} " \
                                    f"AND guild = {owner.guild.id};"
    record = await conn.fetch(get_owner_and_waifu_ids_query)
    if record:
        waifu_id = record[0][0]
        owner_id = record[0][1]
    else:
        await insert_waifu(owner, conn)
        waifu_id = owner.id
        owner_id = None
    return waifu_id, owner_id


async def get_waifu_stats_from_db(guild: Guild, waifu_id: int, conn: asyncpg.Connection) -> WaifuStats:
    guild = guild
    guild_id = guild.id

    get_waifu_info_query = "SELECT energy, speed, profit, luck, strength, cost, lover, working_status, " \
                           "resting_status, gift_status " \
                           "FROM waifu_stats " \
                           f"WHERE guild = {guild_id} AND user_id = {waifu_id}"
    waifu_info_record = await conn.fetch(get_waifu_info_query)
    waifu_list_info = waifu_info_record[0]

    energy = waifu_list_info[0]
    speed = waifu_list_info[1]
    profit = waifu_list_info[2]
    luck = waifu_list_info[3]
    strength = waifu_list_info[4]
    cost = waifu_list_info[5]
    lover = waifu_list_info[6]
    is_working = waifu_list_info[7]
    is_resting = waifu_list_info[8]
    is_gift_ready = waifu_list_info[9]

    try:
        member = await guild.fetch_member(waifu_id)
    except discord.NotFound:
        await delete_waifu(waifu_id=waifu_id, guild=guild)
        raise WaifuNotFound(waifu_id)

    waifu_stats = WaifuStats(member=member, energy=energy, speed=speed, profit=profit, luck=luck,
                             strength=strength, cost=cost, lover_user=lover, is_working=is_working,
                             is_resting=is_resting, is_gift_ready=is_gift_ready)
    return waifu_stats


async def get_waifus_from_db(owner: Member, conn: asyncpg.Connection) -> List[asyncpg.Record]:
    guild_id = owner.guild.id
    owner_id = owner.id
    get_waifus_list_query = "SELECT waifu " \
                            "FROM waifus " \
                            f"WHERE guild = {guild_id} AND owner = {owner_id}"
    waifu_records = await conn.fetch(get_waifus_list_query)

    return waifu_records

# Insert


async def add_waifu(owner: Member, member: Member) -> WaifuStats:
    conn = await asyncpg.connect(Database.str_connection)
    update_or_insert_waifu_sql = "DO $$ " \
                                 "BEGIN " \
                                    "IF EXISTS(" \
                                    "SELECT * FROM waifus " \
                                    f"WHERE guild = {member.guild.id} AND waifu = {member.id}) THEN " \
                                        f"UPDATE waifus SET owner = {owner.id} " \
                                        f"WHERE guild = {member.guild.id} AND waifu = {member.id}; " \
                                    f"ELSE " \
                                        f"INSERT INTO waifus (guild, owner, waifu) " \
                                        f"VALUES ({member.guild.id}, {owner.id}, {member.id}); " \
                                        f"INSERT INTO waifu_stats (guild, user_id) " \
                                        f"VALUES ({member.guild.id}, {member.id}); " \
                                 f"END IF;" \
                                 f"END $$;"
    await conn.fetch(update_or_insert_waifu_sql)
    stats = await get_waifu_stats_from_db(member.guild, member.id, conn)
    return stats


async def remove_owner(waifu: Member, conn: asyncpg.Connection):
    waifu_id = waifu.id
    remove_owner_from_waifu_query = f"UPDATE waifus SET owner = NULL WHERE waifu = {waifu_id} " \
                                    f"AND guild = {waifu.guild.id};"
    await conn.fetch(remove_owner_from_waifu_query)


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
                             strength: int = None, luck: int = None) -> bool:
    conn = await asyncpg.connect(Database.str_connection)
    await insert_waifu(member, conn)
    update_attrs_beginning_query = f"UPDATE waifu_stats SET "
    update_attrs_query = ""
    if speed:
        update_attrs_query += f"speed = {speed}, "
    if energy:
        update_attrs_query += f"energy = {energy}, "
    if profit:
        update_attrs_query += f"profit = {profit}, "
    if strength:
        update_attrs_query += f"strength = {strength}, "
    if luck:
        update_attrs_query += f"luck = {luck}, "

    if update_attrs_query is "":
        return False

    update_attrs_query = update_attrs_query[:-2] + " "

    update_attrs_ending_query = f"WHERE guild = {member.guild.id} AND user_id = {member.id};"
    result_query = update_attrs_beginning_query + update_attrs_query + update_attrs_ending_query
    await conn.fetch(result_query)
    return True


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


async def upgrade_attributes(member: Member, randomizer: Randomizer, levels: int):
    conn = await asyncpg.connect(Database.str_connection)
    for i in enumerate(range(levels)):
        result = randomizer.run()
        await upgrade_attribute(member, result, conn)
    await conn.close()


async def upgrade_attribute(member: Member, index: int, conn: asyncpg.Connection):
    attr_name = attr_dict[index]
    increment_attribute_query = f"UPDATE waifu_stats SET {attr_name} = (SELECT {attr_name} FROM waifu_stats " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}) + 1 " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(increment_attribute_query)


async def update_cost_of_waifu(member: Member, level_cost: int):
    conn = await asyncpg.connect(Database.str_connection)
    update_cost_of_waifu_query = f"UPDATE waifu_stats SET cost = (SELECT cost FROM waifu_stats " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}) + {level_cost} " \
                                f"WHERE guild = {member.guild.id} AND user_id = {member.id}"
    await conn.fetch(update_cost_of_waifu_query)
    await conn.close()


async def update_working_status(interacting: Member, waifu: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)

    try:
        await check_owner(interacting, waifu, conn)
    except InteractingNotOwner:
        return
    except OwnerDoesNotExist:
        return

    update_working_status_query = f"UPDATE waifu_stats SET working_status = {status} " \
                                  f"WHERE guild = {waifu.guild.id} AND user_id = {waifu.id}"
    await conn.fetch(update_working_status_query)
    await conn.close()


async def update_resting_status(interacting: Member, waifu: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)

    try:
        await check_owner(interacting, waifu, conn)
    except InteractingNotOwner:
        return
    except OwnerDoesNotExist:
        return

    update_resting_status_query = f"UPDATE waifu_stats SET resting_status = {status} " \
                                  f"WHERE guild = {waifu.guild.id} AND user_id = {waifu.id}"
    await conn.fetch(update_resting_status_query)
    await conn.close()


async def update_gift_status(interacting: Member, waifu: Member, status: bool):
    conn = await asyncpg.connect(Database.str_connection)

    try:
        await check_owner(interacting, waifu, conn)
    except InteractingNotOwner:
        return
    except OwnerDoesNotExist:
        return

    update_gift_status_query = f"UPDATE waifu_stats SET gift_status = {status} " \
                                  f"WHERE guild = {waifu.guild.id} AND user_id = {waifu.id}"
    await conn.fetch(update_gift_status_query)
    await conn.close()

