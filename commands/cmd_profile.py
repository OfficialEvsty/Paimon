import base64
from PIL import Image
import discord
import discord.app_commands
from card_profile.profile import Profile
from card_profile.premium_profile import Premium_Profile
from discord import File as dFile
from bot import Bot
from io import BytesIO
from utilities.gif_creator.gif import get_img_file, convert_to_bytea, Gif, get_gif_frames
import asyncpg
import base64
import psycopg2
import aiohttp
import re
from bot_ui_kit.ui_profile_interaction import UI_ProfileView


async def cmd_card(interaction: discord.Interaction, user: discord.Member = None) -> None:

    await interaction.response.defer()

    if user is None:
        user = interaction.user

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{user.avatar}?size=1024') as resp:
            profile_bytes = await resp.read()
    guild_id = interaction.guild.id
    user_id = user.id
    select_users_join_visions_join_premium_join_files = \
                                "SELECT xp, rank, uid, bio, namecard, visions.vision, premium_users.id, files.gif " \
                                "FROM users " \
                                "LEFT JOIN visions ON users.id = visions.user_id " \
                                "LEFT JOIN premium_users ON users.id = premium_users.user_id " \
                                "LEFT JOIN files ON users.id = files.user_id " \
                                f"WHERE users.guild = {guild_id} AND users.id = {user_id}"
    conn = await asyncpg.connect(Bot.db.str_connection)
    result = await conn.fetch(select_users_join_visions_join_premium_join_files)
    await conn.close()

    if not result:
        return await interaction.response.send_message("Прежде чем пользоваться этой командой, хотя бы поприветствуйте всех на сервере.", delete_after=5, ephemeral=True)

    xp = result[0][0]
    rank = result[0][1]
    uid = result[0][2]
    bio = result[0][3]
    card = result[0][4]
    vision = result[0][5]
    premium = result[0][6]

    if uid is None:
        uid = "Не ввёден"
    if bio is None:
        bio = "Обычное описание, как и у всех."
    if vision is None:
        vision = None

    view = await UI_ProfileView(user=user).create_view()

    if premium:
        encoded_gif = result[0][7]
        if encoded_gif:
            gif = get_gif_frames(decode_file(encoded_gif))
            profilecard = Premium_Profile(gif)

            buffer = profilecard.draw(str(user), uid, bio, rank, xp, BytesIO(profile_bytes), vision=vision, premium=premium)

            if interaction.message:
                return await interaction.followup.edit_message(message_id=interaction.message.id,
                                                               attachments=[dFile(fp=buffer, filename='rank_card.gif')],
                                                               view=view)

            return await interaction.followup.send(file=dFile(fp=buffer, filename='rank_card.gif'), view=view)
    else:
        profilecard = Profile()

        buffer = profilecard.draw(str(user), uid, bio, rank, xp, BytesIO(profile_bytes), card, vision, premium)

        if interaction.message:
            return await interaction.followup.edit_message(message_id=interaction.message.id, attachments=[dFile(fp=buffer, filename='rank_card.png')], view=view)

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


def encode_file():
    pass

def decode_file(encoded_buffer) -> BytesIO:
    b64decode_buffer = base64.b64decode(encoded_buffer)
    return BytesIO(b64decode_buffer)

async def cmd_get_animated_profile(interaction: discord.Interaction):
    user = interaction.user
    user_id = user.id
    guild = interaction.guild.id
    get_gif_sql_query = f'SELECT gif FROM files WHERE guild = {guild} AND user_id = {user_id}'
    conn = await asyncpg.connect(Bot.db.str_connection)
    result = await conn.fetch(get_gif_sql_query)
    await conn.close()
    if result:
        encoded_buffer = result[0][0]

        gif_frames = []
        gif = get_gif_frames(decode_file(encoded_buffer))
        frames = gif.frames_IO
        for frame in frames:
            im = Image.open(frame).convert("RGBA")
            black_shape = Image.new(mode="RGBA", color=(10, 100, 42, 255), size=(im.size[0] // 2, im.size[1] // 2))
            im.paste(black_shape, mask=black_shape)
            gif_frames.append(im)
        gif.frames = gif_frames

        buffer = gif.construct()
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="gif.gif")
        await interaction.followup.send(file=file)

async def cmd_set_animated_profile(interaction: discord.Interaction, gif_url: str):
    user = interaction.user
    user_id = user.id
    guild = interaction.guild.id
    bytes_ = convert_to_bytea(get_img_file(gif_url))
    b64_img = base64.b64encode(bytes_.getvalue())
    b64_img = psycopg2.Binary(b64_img)


    add_or_insert_gif_query = 'DO $$ ' \
                              'BEGIN ' \
                                    f'IF EXISTS (' \
                                    f'SELECT * FROM files ' \
                                    f'WHERE user_id = {user_id} AND guild = {guild}) THEN ' \
                                        f"UPDATE files SET gif = {b64_img}::bytea " \
                                        f'WHERE user_id = {user_id} AND guild = {guild};' \
                                    f'ELSE ' \
                                        f'INSERT INTO files (user_id, guild, gif) ' \
                                        f"VALUES ({user_id}, {guild}, {b64_img}::bytea);" \
                                    f'END IF;' \
                              f'END $$;'
    conn = await asyncpg.connect(Bot.db.str_connection)
    await conn.fetch(add_or_insert_gif_query)
    await conn.close()
    await interaction.followup.send("Файл загружен")



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






