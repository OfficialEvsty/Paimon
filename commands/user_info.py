import time

import discord
import discord.app_commands
from utilities.embeds.paimon import Paimon_Embed
from bot import Bot








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

async def cmd_take_money(*kwargs):
    pass





async def cmd_get_uid(interaction: discord.Interaction):
    # args for sql query
    table = "users"
    user = interaction.user
    user_id = user.id
    col_uid = "uid"
    col_guild = "guild"
    guild_id = interaction.guild.id

    condition_pattern = "AND"
    dict_conditions = {"id" : user_id, col_guild : guild_id}
    results = await Bot.db.get_db(table, await Bot.db.filter(condition_pattern, dict_conditions), [col_uid, "id"])

    if not results[0][0]:
        return await interaction.response.send_message("Пользователь не зарегистрировал UID.")
    uid = results[0][0]
    p_embed = Paimon_Embed().construct("UID command", str(user) + " UID's:" + str(uid))
    await interaction.response.send_message(embed=p_embed)

"""async def cmd_bio(interaction: discord.Interaction, text: str):
    field_name = 'bio'
    user_id = interaction.user.id
    table = 'users'
    content = text
    col_guild = "guild"
    guild_id = interaction.guild.id
    if bio_validation(content):
        text = f"{content}"
        val = "'" + text + "'"
        condition_pattern = "AND"
        dict_conditions = {"id" : user_id, col_guild : guild_id}
        dict_container = {"id" : user_id, field_name : val, col_guild : guild_id}
        is_success = await Bot.db.set_db(table=table, conditions_str=await Bot.db.filter(condition_pattern, dict_conditions),
                                                                      dict_col_val=dict_container)
        if not is_success:
            await Bot.db.update_db(table=table, conditions_str=await Bot.db.filter(condition_pattern, dict_conditions),
                                dict_col_val=dict_container)
        return await interaction.response.send_message("Подпись сохранена.")
    return await interaction.response.send_message(f"Минимальное количество символом - 1, Максимальное количество - 100.")"""








