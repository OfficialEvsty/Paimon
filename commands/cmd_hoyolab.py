from data.database import Database
from hoyolab.genshin_statistics.genshin_user import Genshin_User as G_user
from hoyolab.hoyolab_user import Hoyolab
from gui.genshin_gui import Genshin_GUI as GGUI
from gui.hoyolab_gui import Hoyolab_GUI
from bot_ui_kit.ui_hoyolab_interaction import UI_HoyolabView
import asyncpg
import discord
import genshin


async def profile_hoyolab(interaction: discord.Interaction, user: discord.User = None):
    if user is not None:
        user = user
    else:
        user = interaction.user

    cookies = await get_cookies(user)
    hoyolab = Hoyolab(cookies)
    await hoyolab.init()
    buffer = Hoyolab_GUI().draw(hoyolab.user.bg_url, hoyolab.user.icon, hoyolab.user.nickname,
                                hoyolab.user.level.level, hoyolab.cookies["ltuid"])
    dFile = discord.File(fp=buffer, filename="genshin_profile.png")

    ui = UI_HoyolabView(user, hoyolab)
    view = await ui.create_view()


    message = interaction.message
    if message:
        message_id = message.id
        await interaction.followup.edit_message(message_id=message_id, attachments=[dFile], view=view)
    else:
        pass

async def get_cookies(user: discord.User) -> {}:
    user_id = user.id
    get_hoyolab_data_query = f'SELECT ltuid, ltoken FROM hoyolab_data WHERE user_id = {user_id}'
    conn = await asyncpg.connect(Database.str_connection)
    result = await conn.fetch(get_hoyolab_data_query)
    await conn.close()
    if result:
        ltuid = result[0][0]
        ltoken = result[0][1]
        return {"ltuid": ltuid, "ltoken": ltoken}
    return None



async def get_hoyolab_stats(interaction: discord.Interaction):
    user_id = interaction.user.id
    get_hoyolab_data_query = f'SELECT ltuid, ltoken FROM hoyolab_data WHERE user_id = {user_id}'
    conn = await asyncpg.connect(Database.str_connection)
    result = await conn.fetch(get_hoyolab_data_query)
    await conn.close()
    if result:
        ltuid = result[0][0]
        ltoken = result[0][1]
        hoyolab = Hoyolab(ltuid, ltoken)
        await hoyolab.init()
        g_user = G_user(hoyolab)
        await g_user.init()

        await interaction.followup.send(g_user.show())


async def valide_hoyolab(ltuid: int, ltoken: str) -> bool:
    cookies = {"ltuid": ltuid, "ltoken": ltoken}
    is_valid = True
    try:
        client = genshin.Client(cookies)
        genshin_user = await client.get_genshin_user(client.uid)
    except genshin.errors.InvalidCookies:
        is_valid = False
    return is_valid


async def add_hoyolab(user: discord.User, ltuid: int, ltoken: str) -> bool:
    user_id = user.id
    if not await valide_hoyolab(ltuid, ltoken):
        print("Hoyolab ID's not valid.")
        return False
    conn = await asyncpg.connect(Database.str_connection)
    add_if_not_exist_if_exist_update = "DO $$ " \
                                       "BEGIN " \
                                            "IF EXISTS (" \
                                            "SELECT user_id FROM hoyolab_data " \
                                            f"WHERE user_id = {user_id}) THEN " \
                                                f"UPDATE hoyolab_data SET ltuid = {ltuid}, ltoken = '{ltoken}' " \
                                                f"WHERE user_id = {user_id};" \
                                            f"ELSE " \
                                                f"INSERT INTO hoyolab_data (user_id, ltuid, ltoken) " \
                                                f"VALUES ({user_id}, {ltuid}, '{ltoken}');" \
                                            f"END IF;" \
                                       f"END $$;"
    await conn.fetch(add_if_not_exist_if_exist_update)
    await conn.close()
    return True


async def has_hoyolab(user: discord.User) -> bool:
    user_id = user.id
    conn = await asyncpg.connect(Database.str_connection)
    on_check_user_in_hoyolab_db_query = f"SELECT * FROM hoyolab_data WHERE user_id = {user_id}"
    result = await conn.fetch(on_check_user_in_hoyolab_db_query)
    if result:
        return True
    else:
        return False
