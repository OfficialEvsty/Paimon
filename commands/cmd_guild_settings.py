import discord
import asyncpg
from data.database import Database


async def set_notifications_channel_id(interaction: discord.Interaction, is_disabled):
    channel_id = "NULL"
    if not is_disabled:
        channel_id = interaction.channel_id
    guild = interaction.guild.id

    set_or_update_notifications_channel_id_query = "DO $$ " \
                                                     "BEGIN " \
                                                        "IF EXISTS " \
                                                            "(SELECT users_notify_channel_id " \
                                                            "FROM guilds " \
                                                            f"WHERE id = {guild}) THEN " \
                                                                f"UPDATE guilds " \
                                                                f"SET users_notify_channel_id = {channel_id} " \
                                                                f"WHERE id = {guild}; " \
                                                        f"ELSE " \
                                                            f"INSERT INTO guilds (id, users_notify_channel_id) VALUES ({guild}, {channel_id});" \
                                                        f"END IF;" \
                                                   f"END $$;"

    conn = await asyncpg.connect(Database.str_connection)
    await conn.fetch(set_or_update_notifications_channel_id_query)
    await conn.close()
    print(f"Channel {channel_id} set up as notifications channel.")

async def set_transactions_channel_id(interaction: discord.Interaction, is_disabled):
    channel_id = "NULL"
    if not is_disabled:
        channel_id = interaction.channel_id
    guild = interaction.guild.id

    set_or_update_transactions_channel_id_query = "DO $$ " \
                                                     "BEGIN " \
                                                        "IF EXISTS " \
                                                            "(SELECT transactions_channel_id " \
                                                            "FROM guilds " \
                                                            f"WHERE id = {guild}) THEN " \
                                                                f"UPDATE guilds " \
                                                                f"SET transactions_channel_id = {channel_id} " \
                                                                f"WHERE id = {guild}; " \
                                                        f"ELSE " \
                                                            f"INSERT INTO guilds (id, transactions_channel_id) VALUES ({guild}, {channel_id});" \
                                                        f"END IF;" \
                                                   f"END $$;"

    conn = await asyncpg.connect(Database.str_connection)
    await conn.fetch(set_or_update_transactions_channel_id_query)
    await conn.close()
    print(f"Channel {channel_id} set up as transactions channel.")


async def get_notifications_channel(guild: discord.Guild) -> discord.TextChannel:
    conn = await asyncpg.connect(Database.str_connection)
    select_notifications_channel_id_query = f"SELECT users_notify_channel_id FROM guilds WHERE id = {guild.id}"
    result = await conn.fetch(select_notifications_channel_id_query)
    await conn.close()
    if result:
        for channel in guild.channels:
            if channel.id == result[0][0]:
                return channel
    return None

async def get_transactions_channel(guild: discord.Guild) -> discord.TextChannel:
    conn = await asyncpg.connect(Database.str_connection)
    select_transactions_channel_id_query = f"SELECT transactions_channel_id FROM guilds WHERE id = {guild.id}"
    result = await conn.fetch(select_transactions_channel_id_query)
    await conn.close()
    if result:
        for channel in guild.channels:
            if channel.id == result[0][0]:
                return channel
    return None


