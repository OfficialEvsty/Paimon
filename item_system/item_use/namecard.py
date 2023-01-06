import discord
import asyncpg
import json
import random
from item_system.item_use import usage
from item_system.item import Item
from bot import Bot
from item_system.generator import Generator
from rewarding.reward import Reward
from transaction_system.transaction import Transaction


@usage.add_item_use
async def namecard(interaction: discord.Interaction, item: Item):
    pattern = "_Item.png"
    path = "item_system/item_images/"
    name = item.img_url.replace(pattern, "").replace(path, "")
    user = interaction.user
    user_id = user.id
    Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
    on_insert_name_query = f"INSERT INTO namecards (user_id, namecard) SELECT {user_id}, '{name}' " \
                           f"WHERE NOT EXISTS (SELECT namecard FROM namecards WHERE namecard = '{name}' AND user_id = {user_id});"
    await Bot.db.conn.fetch(on_insert_name_query)
    await Bot.db.conn.close()

    """msg = f"{user} добавил новую именную карту '{name}' в коллекцию, её можно использовать в профиле."
    await interaction.response.follow(msg, delete_after=5)"""


@usage.add_item_use
async def vision(interaction: discord.Interaction, item: Item):
    user_id = interaction.user.id
    guild = interaction.guild.id
    path = "item_system/item_images/visions/"
    format_file = ".png"

    vision_name = item.img_url.replace(path, "").replace(format_file, "")
    item_id = item.id

    Bot.db.conn = await asyncpg.connect(Bot.db.str_connection)
    on_insert_vision_query = f"DO $$ " \
                                f"BEGIN " \
                                    f"IF NOT EXISTS (" \
                                        f"SELECT * FROM visions " \
                                        f"WHERE user_id = {user_id} AND guild = {guild}) THEN " \
                                            f"INSERT INTO visions (user_id, guild, vision, item_id) " \
                                            f"VALUES ({user_id}, {guild}, '{vision_name}', {item_id}); " \
                                    f"ELSE " \
                                        f"DELETE FROM visions WHERE user_id = {user_id} AND guild = {guild};" \
                                        f"INSERT INTO visions (user_id, guild, vision, item_id) " \
                                            f"VALUES ({user_id}, {guild}, '{vision_name}', {item_id});" \
                                    f"END IF;" \
                                f"END $$;"
    await Bot.db.conn.fetch(on_insert_vision_query)
    await Bot.db.conn.close()


@usage.add_item_use
async def wishing(interaction: discord.Interaction, item: Item):
    user = interaction.user
    guild = interaction.guild
    min_money = 50
    max_money = 500

    money = random.randint(min_money, max_money)
    list_items = []
    with open("item_system/item_use/wishing.json", "r") as file:
        group_type_chance_drop_dict = json.loads(file.read())
    for (type, chance) in group_type_chance_drop_dict.items():
        result = random.random()
        print(result, chance)
        if result <= chance:
            items = Generator.generate_random_items_by_group_type(type, 1)
            list_items.extend(items)

    reward = Reward(guild, user, money, items=list_items)
    await reward.apply()

    reason = f"{user} помолился, использовав {item.name}"
    transaction = Transaction(user, reason, money, received_items=list_items)
    await transaction.send()





