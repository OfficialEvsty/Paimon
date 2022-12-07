import time

from main import bot
import re
from .profile import Profile
from discord import File as dFile
from io import BytesIO
import aiohttp


async def cmd_card(*kwargs) -> None:

    start = time.monotonic()
    msg = kwargs[0]
    user = msg.author

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{user.avatar}?size=512') as resp:
            profile_bytes = await resp.read()

    result = await bot.db.fetch(f"SELECT xp, rank, uid, bio FROM users WHERE id = {user.id}")
    validation = result[0][0] == None or result[0][1] == None or result[0][2] == None or result[0][3] == None
    if validation:
        return await msg.channel.send(f'{user} ещё не зарегистрирован в Гильдии искателей приключений.')

    xp = result[0][0]
    rank = result[0][1]
    uid = result[0][2]
    bio = result[0][3]

    profilecard = Profile()
    buffer = profilecard.draw(str(user), uid, bio, rank, xp, BytesIO(profile_bytes))
    end = time.monotonic()
    print("cmd_card", end - start)

    return await msg.channel.send(file=dFile(fp=buffer, filename='rank_card.png'))
#сделать валидаторы для команд
async def cmd_give_money(*kwargs):
    field_name = 'coins'
    msg = kwargs[0]
    user = msg.author
    user_id = user.id

    user_to_give = user_id
    amount = kwargs[1][0]

    current_amount = await get_db(user_to_give, field_name)
    general_amount = int(current_amount) + int(amount)
    await set_db(user_to_give, field_name, general_amount)
    await msg.channel.send(f"{amount} добавлено на счет {user}. Общий счёт: {general_amount}")

async def cmd_take_money(*kwargs):
    pass

async def cmd_set_uid(*kwargs):
    field_name = 'uid'
    msg = kwargs[0]
    if len(kwargs) < 2:
        await msg.channel.send("Необходимо ввести UID. set_uid [7-------]")
    uid = kwargs[1][0]
    if not uid_validation(uid):
        await msg.channel.send("Неверный формат UID. Правильным форматом является 9 значное число, начинающееся с цифры 7.")
    user_id = str(msg.author.id)
    await set_db(user_id, field_name, uid)
    await msg.channel.send("UID успешно сохранен.")

async def cmd_bio(*kwargs):
    field_name = 'bio'
    msg = kwargs[0]
    user_id = msg.author.id

    if len(kwargs) < 2:
        return await msg.channel.send("Неправильные входные данные. Правильный формат bio Ваш текст.")
    content = " ".join(kwargs[1:][0])
    if bio_validation(content):
        text = f"{content}"
        val = "'" + text + "'"
        await set_db(user_id, field_name, val)
        return await msg.channel.send("Подпись сохранена.")
    return await msg.channel.send("Минимальное количество символом - 1, Максимальное количество - 60.")


def uid_validation(text):
    regex = r'^7\d{8}$'
    return bool(re.match(regex, str(text)))

def bio_validation(text):
    if len(text) <= 60 and len(text) > 0 : return bool

async def cmd_get_uid(*kwargs):
    msg = kwargs[0]
    if len(kwargs) < 2:
        user_id = str(msg.author.id)
        user = msg.author
    else:
        user = kwargs[1][0]
        user_id = user[2:len(user) - 1]
        print(user_id)
    uid = await get_db(user_id, "uid")

    if uid == None:
        return "Пользователь не зарегистрировал UID."

    await msg.channel.send(str(user) + " UID's:" + str(uid))


async def get_db(user_id, string):
    col = string
    table = "users"
    is_user_in_db = f"SELECT FROM users WHERE id = {user_id}"
    if not await bot.db.fetch(is_user_in_db):
        return None
    sql_query = f"SELECT {col} FROM users WHERE id = {user_id}"
    result = await bot.db.fetch(sql_query)
    if result:
        return result[0][0]
    else:
        return None


async def set_db(user_id, string, value):
    col = string
    val = value
    table = "users"
    is_user_exists = f'SELECT id FROM users WHERE id = {user_id}'
    sql_update = f'UPDATE users SET {col} = {val} WHERE id = {user_id}'
    sql_query = f'INSERT INTO {table} (id, {col}) ' \
                f'VALUES ({user_id}, {val})'
    result = await bot.db.fetch(is_user_exists)
    if result[0][0] != None:
        await bot.db.fetch(sql_update)
    else:
        await bot.db.fetch(sql_query)