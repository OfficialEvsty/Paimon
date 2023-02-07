import discord
from discord.webhook import Webhook
import commands.cmd_main
import item_system.item
from trade_system.trade import Trade
from trade_system.gift import Gift
from utilities.embeds.inventory import Inventory_Embed
from item_system.generator import Generator
from item_system.item import Item
from item_system.inventory_gui import Inventory_GUI as GUI
from bot_ui_kit.ui_interventory import UI_InterventoryView
from bot_ui_kit.ui_creating_trade_interaction import UI_CreatingTradeView
from item_system.interventory import Interventory
from bot import Bot


# Opens inventory of user who called the command and shows him his items.
async def show_inventory(interaction: discord.Interaction, is_private: bool, inter_history = None):
    owner = interaction.user

    await interaction.response.defer(ephemeral=is_private)
    records_item = await Interventory.get_inventory(interaction)

    if records_item:
        if inter_history is None:
            interventory = Interventory(Generator.create_items(Generator.to_list(records_item)))
        else:
            interventory = Interventory(Generator.create_items(Generator.to_list(records_item)), inter_history)
        gui = GUI(interventory.stack_store)
        buffer = gui.draw()

        ui = UI_InterventoryView(user=owner, interventory=interventory)

        file = discord.File(fp=buffer, filename="inventory.png")

        description = "Выберите предмет, чтобы увидеть его описание."

        embed = Inventory_Embed(
            interaction=interaction,
            description=description,
            image_url=f"attachment://inventory.png"
        )

        if interaction.message is not None:
            webhook_id = interaction.message.id
            original = await interaction.followup.edit_message(message_id=webhook_id, attachments=[file], embed=embed, view=ui)
            ui.original = original
            return

        original = await interaction.followup.send(file=file, embed=embed, view=ui)
        ui.original = original
    else:
        if interaction.message:
            webhook_id = interaction.message.id
            await interaction.followup.delete_message(webhook_id)
            await interaction.followup.send("Ваш инвентарь пуст.")
        else:
            await interaction.followup.send("Ваш инвентарь пуст.")


# Opens inventory of user in trade mode.
async def show_trade_inventory(interaction: discord.Interaction, view: discord.ui.View = None,
                               interventory: Interventory = None, chosen_item: int = None):

    await interaction.response.defer()
    if interventory is None:
        records_item = await Interventory.get_inventory(interaction)
        interventory = Interventory(Generator.create_items(Generator.to_list(records_item)))
        gui = GUI(interventory.stack_store, interventory.trade_items)
        buffer = gui.draw()

        ui = UI_CreatingTradeView(user=interaction.user, interventory=interventory)

        file = discord.File(fp=buffer, filename="inventory.png")
        description = "Выберите предмет, чтобы добавить его в трейд лист."
        embed = Inventory_Embed(
            interaction=interaction,
            description=description,
            image_url=f"attachment://inventory.png"
        )

        if interaction.message:
            message_id = interaction.message.id
            original = await interaction.followup.edit_message(message_id=message_id, embeds=[embed], attachments=[file], view=ui)
            ui.original = original
            return
    elif interventory.trade_items is not None:

        gui = GUI(dict_items=interventory.stack_store, dict_items_to_trade=interventory.trade_items)

        if chosen_item:
            buffer = gui.draw(chosen_item=chosen_item, is_trade_mode=True)
        else:
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
            original = await interaction.followup.edit_message(message_id=message_id, embed=embed, attachments=[file], view=view)
            view.original = original
            return


"""async def on_switch_page(interaction: discord.Interaction, items_page: [], view: discord.ui.View, inventory: Inventory):
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
        return await interaction.followup.edit_message(message_id=message_id, attachments=[file], embed=embed, view=view)"""


async def on_switch_page_select(interaction: discord.Interaction, view: discord.ui.View, interventory: Interventory):
    items = interventory.stack_store
    gui = GUI(dict_items=items)
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


async def switch_view(interaction: discord.Interaction, view: discord.ui.View):
    if interaction.message:
        await interaction.response.edit_message(view=view)


async def draw_inventory_edit(interaction: discord.Interaction, dict_items: {}, view: discord.ui.View, chosen_item: int = None):
    await interaction.response.defer()
    if len(dict_items) > 0:
        gui = GUI(dict_items)
        buffer = gui.draw(chosen_item=chosen_item)

        if chosen_item:
            description = f"**Описание**\n>>> {dict_items[chosen_item][0].description}"
            embed = Inventory_Embed(
                interaction=interaction,
                description=description,
                image_url=f"attachment://inventory.png"
            ).insert_field_at(
                0, name="**Расходуемый**", value=f">>> {'Да' if dict_items[chosen_item][0].consumable else 'Нет'}"
            ).insert_field_at(
                0, name="**Складируемый**", value=f">>> {'Да' if dict_items[chosen_item][0].stackable else 'Нет'}"
            )
        else:
            description = "Выберите предмет, чтобы увидеть его описание."
            embed = Inventory_Embed(
                interaction=interaction,
                description=description,
                image_url=f"attachment://inventory.png")
    if interaction.message:
        message_id = interaction.message.id
        await interaction.followup.edit_message(message_id=message_id, embed=embed,
                                                attachments=[discord.File(fp=buffer, filename="inventory.png")],
                                                view=view)
    else:
        await interaction.response.send_message("Ваш инвентарь пуст.")


async def drop(items: []):
    await Interventory.remove_items(items)


async def gift(interaction: discord.Interaction, interventory: Interventory, recipient: discord.User, timer: int = None):
    user = interaction.user
    guild = interaction.guild
    items = interventory.trade_items

    list_items = pull_items_from_dict(items)

    gift_query = Gift(user, guild, recipient, items, timer)

    await Interventory.withdraw_items_from_inventory(guild, list_items)

    await gift_query.send()


async def trade(interaction: discord.Interaction, interventory: Interventory, money: int = None, timer: int = None,
                user_receiving_items: discord.User = None):
    user = interaction.user
    guild = interaction.guild
    items = interventory.trade_items

    list_items = pull_items_from_dict(items)

    trade_query = Trade(owner_user=user, items=items, money=money, timer=timer)

    await Interventory.withdraw_items_from_inventory(guild, list_items)

    await trade_query.create_trade(interaction)


def pull_items_from_dict(dict_: {}) -> []:
    list_items = []
    for slot in dict_.values():
        for item in slot:
            list_items.append(item)
    return list_items
