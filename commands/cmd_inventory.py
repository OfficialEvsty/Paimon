import discord
from item_system.generator import Generator
from item_system.inventory import Inventory
from item_system.inventory_gui import Inventory_GUI as GUI
from bot import Bot

async def buy_item(interaction: discord.Interaction, item_type: bytes):
    """conditions = await Bot.db.filter("AND", {"user_id": interaction.user.id, "guild": interaction.guild.id})
    await Bot.db.add_db(table="items", conditions_str=conditions,
                        dict_col_val={"user_id": interaction.user.id, "guild": interaction.guild.id, "type": item_type})"""

    #await interaction.response.send_message(inventory.show())


async def show_inventory(interaction: discord.Interaction):
    condition_pattern = "AND"
    conditions_dict = {"user_id": interaction.user.id, "guild": interaction.guild.id}
    list_column = ["id", "type"]
    records_item = await Bot.db.get_db(table="items",
                                       conditions_str=await Bot.db.filter(condition_pattern, conditions_dict),
                                       list_col_to_get=list_column)

    inventory = Inventory(Generator.create_items(Generator.to_list(records_item)))
    gui = GUI(inventory.list_items)
    buffer = gui.draw()

    return await interaction.response.send_message(file=discord.File(fp=buffer, filename="inventory.png"))
