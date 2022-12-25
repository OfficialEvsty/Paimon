import discord
import discord.app_commands
from card_profile.profile import Profile
from discord import File as dFile
from bot import Bot
from io import BytesIO
import asyncpg
import aiohttp
import re
from bot_ui_kit.ui_profile_interaction import UI_ProfileView

async def cmd_card(interaction: discord.Interaction, user: discord.Member = None) -> None:

    if user is None:
        user = interaction.user

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{user.avatar}?size=512') as resp:
            profile_bytes = await resp.read()
    table = "users"
    guild_id = interaction.guild.id
    user_id = user.id
    cols_list = ["xp", "rank", "uid", "bio", "namecard", "vision"]
    condition_pattern = "AND"
    dict_conditions = {"id" : user_id, "guild" : guild_id}
    result = await Bot.db.get_db(table, await Bot.db.filter(condition_pattern, dict_conditions), cols_list)

    if not result:
        return await interaction.response.send_message("Прежде чем пользоваться этой командой, хотя бы поприветствуйте всех на сервере.", delete_after=5, ephemeral=True)

    xp = result[0][0]
    rank = result[0][1]
    uid = result[0][2]
    bio = result[0][3]
    card = result[0][4]
    vision = result[0][5]

    if uid is None:
        uid = "Не ввёден"
    if bio is None:
        bio = "Обычное описание, как и у всех."
    if vision is None:
        vision = None

    view = UI_ProfileView(user_id=user_id).create_view()

    profilecard = Profile()
    buffer = profilecard.draw(str(user), uid, bio, rank, xp, BytesIO(profile_bytes), card, vision)

    if interaction.message:
        await interaction.response.defer()
        return await interaction.followup.edit_message(message_id=interaction.message.id, attachments=[dFile(fp=buffer, filename='rank_card.png')], view=view)

    await interaction.response.defer()
    return await interaction.followup.send(file=dFile(fp=buffer, filename='rank_card.png'), view=view)


async def cmd_edit_view(interaction: discord.Interaction, view: discord.ui.View):
    await interaction.message.edit(view=view)
    await interaction.response.defer()


async def cmd_get_user_cards(interaction: discord.Interaction) -> []:
    table = "namecards"
    get_query = f"SELECT namecard FROM {table} WHERE user_id = {interaction.user.id}"
    Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
    result = await Bot.db.conn.fetch(get_query)
    await Bot.db.conn.close()
    cards_list = []
    for record in result:
        cards_list.append(record[0])
    return cards_list


async def cmd_update_user_namecard(interaction: discord.Interaction, namecard: str):
    table = "users"
    print(namecard)
    update_query = f"UPDATE {table} SET namecard = '{namecard}' WHERE id = {interaction.user.id} AND guild = {interaction.guild.id}"
    Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
    await Bot.db.conn.fetch(update_query)
    await Bot.db.conn.close()


def bio_validation(text):
    if len(text) <= 100 and len(text) > 0:
        return bool

async def cmd_set_or_update_bio(interaction: discord.Interaction, text: str):

    column_name = 'bio'
    user_id = interaction.user.id
    table = 'users'
    content = text
    col_guild = "guild"
    guild_id = interaction.guild.id
    if bio_validation(content):
        sql_insert_or_update_query = f"DO $$ " \
                                        f"BEGIN " \
                                            f"IF EXISTS " \
                                                f"( SELECT bio " \
                                                f"FROM users " \
                                                f"WHERE id = {user_id} AND guild = {guild_id}) THEN " \
                                                    f"UPDATE users " \
                                                    f"SET bio = '{content}' " \
                                                    f"WHERE id = {user_id} AND guild = {guild_id}; " \
                                            f"ELSE " \
                                                f"INSERT INTO users (id, guild, bio) VALUES ({user_id}, {user_id}, '{content}');" \
                                        f"END IF;" \
                                     f"END $$;"
        Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
        await Bot.db.fetch(sql_insert_or_update_query)
        await Bot.db.conn.close()


def uid_validation(text):
    regex = r'^7\d{8}$'
    return bool(re.match(regex, str(text)))

async def cmd_set_or_update_uid(interaction: discord.Interaction, _uid: int):
    uid = _uid
    guild_id = interaction.guild.id

    if not uid_validation(uid):
        return await interaction.response.send_message("Неверный формат UID. Правильным форматом является 9 значное число, начинающееся с цифры 7.")
    user_id = interaction.user.id

    sql_insert_or_update_query = f"DO $$ " \
                                    f"BEGIN " \
                                        f"IF EXISTS " \
                                        f"( SELECT uid " \
                                        f"FROM users " \
                                        f"WHERE id = {user_id} AND guild = {guild_id}) THEN " \
                                            f"UPDATE users " \
                                            f"SET uid = '{uid}' " \
                                            f"WHERE id = {user_id} AND guild = {guild_id}; " \
                                        f"ELSE " \
                                            f"INSERT INTO users (id, guild, uid) VALUES ({user_id}, {user_id}, '{uid}');" \
                                        f"END IF;" \
                                 f"END $$;"
    Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
    await Bot.db.fetch(sql_insert_or_update_query)
    await Bot.db.conn.close()






