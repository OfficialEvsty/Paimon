import discord
import discord.app_commands
from utilities.embeds.paimon import Paimon_Embed
import asyncpg
from bot import Bot


async def turn_of_or_on_animated_background(user: discord.User, guild: discord.Guild) -> bool:
    user_id = user.id
    guild = guild.id
    conn = await asyncpg.connect(Bot.db.str_connection)
    switch_background_setting_sql = "DO $$ " \
                                    "BEGIN " \
                                        "IF (" \
                                        "SELECT id::BOOLEAN FROM user_settings " \
                                        f"WHERE user_id = {user_id} AND guild = {guild}) THEN " \
                                            f"IF (SELECT is_premium_background FROM user_settings " \
                                            f"WHERE user_id = {user_id} AND guild = {guild} AND " \
                                            f"is_premium_background = TRUE) THEN " \
                                                f"UPDATE user_settings SET is_premium_background = FALSE " \
                                                f"WHERE user_id = {user_id} AND guild = {guild};" \
                                            f"ELSE " \
                                                f"UPDATE user_settings SET is_premium_background = TRUE " \
                                                f"WHERE user_id = {user_id} AND guild = {guild};" \
                                            f"END IF;" \
                                        f"ELSE " \
                                            f"INSERT INTO user_settings (user_id, guild, is_premium_background) " \
                                            f"VALUES ({user_id}, {guild}, TRUE);" \
                                        f"END IF;" \
                                    f"END $$;"
    print(switch_background_setting_sql)
    get_status_background_setting_sql = f"SELECT is_premium_background FROM user_settings WHERE guild = {guild} " \
                                        f"AND user_id = {user_id}"
    await conn.fetch(switch_background_setting_sql)
    result = await conn.fetch(get_status_background_setting_sql)
    await conn.close()
    return result[0][0]


#сделать валидаторы для команд
async def cmd_give_money(*kwargs):
    field_name = 'coins'
    msg = kwargs[0]
    user = msg.author
    user_id = user.id

    user_to_give = user_id
    amount = kwargs[1][0]

    current_amount = await Bot.db.get_db(user_to_give, field_name)
    general_amount = int(current_amount) + int(amount)
    await Bot.db.set_db(user_to_give, field_name, general_amount)
    await msg.channel.send(f"{amount} добавлено на счет {user}. Общий счёт: {general_amount}")












