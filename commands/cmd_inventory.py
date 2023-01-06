import discord
from discord.webhook import Webhook
import commands.cmd_main
import item_system.item
from trade_system.trade import Trade
from utilities.embeds.inventory import Inventory_Embed
from item_system.generator import Generator
from item_system.inventory import Inventory
from item_system.item import Item
from item_system.inventory_gui import Inventory_GUI as GUI
from bot_ui_kit.ui_inventory_interaction import UI_InventoryView
from bot import Bot


async def switch_page(inventory: Inventory, is_going_to_right_page: bool) -> bool:
    return await inventory.switch_page(is_going_to_right_page)


async def show_inventory(interaction: discord.Interaction, is_private: bool):

    owner_id = interaction.user.id
    if interaction.response and interaction.message is None:
        await interaction.response.defer(ephemeral=is_private)
    records_item = await Inventory.get_inventory(interaction)

    if records_item:
        inventory = Inventory(Generator.create_items(Generator.to_list(records_item)))
        gui = GUI(inventory.list_items_on_page)
        buffer = gui.draw()

        ui = UI_InventoryView(inventory, owner_id)
        view = ui.create_select()

        file = discord.File(fp=buffer, filename="inventory.png")

        description = "Выберите предмет, чтобы увидеть его описание."

        embed = Inventory_Embed(
            interaction=interaction,
            description=description,
            image_url=f"attachment://inventory.png"
        )

        if interaction.message is not None:
            webhook_id = interaction.message.id
            return await interaction.followup.edit_message(message_id=webhook_id, attachments=[file], embed=embed, view=view)

        await interaction.followup.send(file=file, embed=embed, view=view)
    else:
        if interaction.message:
            webhook_id = interaction.message.id
            await interaction.followup.delete_message(webhook_id)
            await interaction.followup.send("Ваш инвентарь пуст.")
        else:
            await interaction.followup.send("Ваш инвентарь пуст.")


async def show_trade_inventory(interaction: discord.Interaction, view: discord.ui.View, items: [] = None, items_to_trade: [] = None,
                               inventory: Inventory = None):
    if interaction.response and interaction.message is None:
        await interaction.response.defer()
    if items is None and items_to_trade is None:
        records_item = await Inventory.get_inventory(interaction)
        inventory = Inventory(Generator.create_items(Generator.to_list(records_item)))
        gui = GUI(inventory.list_items_on_page, items_to_trade)
        buffer = gui.draw()

        file = discord.File(fp=buffer, filename="inventory.png")
        description = "Выберите предмет, чтобы добавить его в трейд лист."
        embed = Inventory_Embed(
            interaction=interaction,
            description=description,
            image_url=f"attachment://inventory.png"
        )

        if interaction.message:
            message_id = interaction.message.id
            return await interaction.followup.edit_message(message_id=message_id, embeds=[embed], attachments=[file], view=view)
    elif items_to_trade is not None:

        gui = GUI(list_items=items, list_items_to_trade=inventory.items_to_trade)
        buffer = gui.draw()

        file = discord.File(fp=buffer, filename="inventory.png")

        description = "Подтвердите трейд лист, чтобы опубликовать трейд в этом канале или отментие его."
        embed = Inventory_Embed(
            interaction=interaction,
            description=description,
            image_url=f"attachment://inventory.png"
        )

        if interaction.message:
            message_id = interaction.message.id
            return await interaction.followup.edit_message(message_id=message_id, embed=embed, attachments=[file], view=view)


async def on_switch_page(interaction: discord.Interaction, items_page: [], view: discord.ui.View, inventory: Inventory):
    gui = GUI(list_items=items_page, list_items_to_trade=inventory.items_to_trade)
    buffer = gui.draw()
    file = discord.File(fp=buffer, filename="inventory.png")
    description = "Подтвердите трейд лист, чтобы опубликовать трейд в этом канале или отментие его."
    embed = Inventory_Embed(
        interaction=interaction,
        description=description,
        image_url=f"attachment://inventory.png"
    )
    await interaction.response.defer()
    if interaction.message:
        message_id = interaction.message.id
        return await interaction.followup.edit_message(message_id=message_id, attachments=[file], embed=embed, view=view)


async def on_switch_page_select(interaction: discord.Interaction, view: discord.ui.View, inventory: Inventory):
    gui = GUI(list_items=inventory.list_items_on_page)
    buffer = gui.draw()
    file = discord.File(fp=buffer, filename="inventory.png")
    description = "Выберите предмет, чтобы увидеть его описание."
    embed = Inventory_Embed(
        interaction=interaction,
        description=description,
        image_url=f"attachment://inventory.png"
    )
    await interaction.response.defer()
    if interaction.message:
        message_id = interaction.message.id
        return await interaction.followup.edit_message(message_id=message_id, attachments=[file], embed=embed, view=view)




async def draw_inventory_edit(interaction: discord.Interaction, list_items: [], chosen_item: int, view: discord.ui.View):
    user_called_id = interaction.user.id
    await interaction.response.defer()
    if len(list_items) > 0:
        gui = GUI(list_items)
        buffer = gui.draw(chosen_item=chosen_item)

        embed = Inventory_Embed(
            interaction=interaction,
            description=list_items[chosen_item].description,
            image_url=f"attachment://inventory.png"
        )
    if interaction.message:
        message_id = interaction.message.id
        inventory_msg = await interaction.followup.edit_message(message_id=message_id, embed=embed, attachments=[discord.File(fp=buffer, filename="inventory.png")], view=view)
    else:
        await interaction.response.send_message("Ваш инвентарь пуст.")
    #return inventory_msg


async def drop(interaction: discord.Interaction, item: item_system.item.Item):
    await Inventory.remove_item(interaction, item.id)


async def trade(interaction: discord.Interaction, inventory: Inventory, money: int, timer: int = None):
    user = interaction.user
    guild = interaction.guild
    items = inventory.items_to_trade

    trade_query = Trade(owner_user=user, items=items, money=money, timer=timer)

    await Inventory.withdraw_items_from_inventory(guild, items)

    await trade_query.create_trade(interaction)
