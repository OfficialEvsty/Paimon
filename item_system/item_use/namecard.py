import discord
import asyncpg
from item_system.item_use import usage
from item_system.item import Item
from bot import Bot


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
