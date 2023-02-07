import discord
from discord.ui import View, Select, UserSelect, Modal, TextInput, Button, Item
from discord import ButtonStyle, TextStyle
from utilities.emojis import Emoji
from item_system.interventory import Interventory
from discord import Interaction, User
from bot_ui_kit.support_entities.listening_blocker_button import ListeningBlocker
import commands

# This class provides interaction over inventory and user


class UI_InterventoryView(View):
    def __init__(self, user: User, interventory: Interventory):
        super(UI_InterventoryView, self).__init__()
        self.owner = user
        self.interventory = interventory
        self.original: discord.Webhook

        self.__select_item__: Select = Select(placeholder="Выбрать предмет", custom_id="Select")
        self.__select_item__.callback = self.__on_selected_item__

        self.__right_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Right_Arrow)
        self.__right_button__.callback = self.__on_right_button_clicked__

        self.__left_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Left_Arrow)
        self.__left_button__.callback = self.__on_left_button_clicked__

        self.__use_button__ = Button(style=ButtonStyle.green, label="Использовать")
        self.__use_button__.callback = self.__on_use_button_clicked__

        self.__trade_button__ = Button(style=ButtonStyle.green, label="Обмен")
        self.__trade_button__.callback = self.__on_trade_clicked__

        self.__drop_button__ = Button(style=ButtonStyle.red, label="Выбросить")
        self.__drop_button__.callback = self.__on_drop_button_clicked__

        self.__back_button__ = Button(style=ButtonStyle.red, label="Назад")

        self.__close_button__ = Button(style=ButtonStyle.red, label="Закрыть")
        self.__close_button__.callback = self.__on_close_button_clicked__

        self.__x1__ = Button(style=ButtonStyle.gray, label="x1")
        self.__x10__ = Button(style=ButtonStyle.gray, label="x10")
        self.__All__ = Button(style=ButtonStyle.gray, label="Все")

        self.__looking_items_preset__ = [self.__left_button__, self.__trade_button__, self.__close_button__,
                                     self.__right_button__, self.__select_item__]
        self.__choose_item_preset__ = [self.__left_button__, self.__use_button__, self.__drop_button__,
                                       self.__back_button__, self.__right_button__, self.__select_item__]
        self.__using_item_preset__ = [self.__left_button__, self.__x1__, self.__x10__,
                                              self.__back_button__, self.__right_button__, self.__select_item__]
        self.__interactive_with_items_preset__ = [self.__left_button__, self.__x1__, self.__x10__, self.__All__,
                                              self.__back_button__, self.__right_button__, self.__select_item__]

        self.__construct__()  # Constructed a view with necessary interaction items for first preview.

    def __construct__(self):
        inter = self.interventory
        self.__right_button__.disabled = not inter.is_any_items_in_next_items()
        self.__left_button__.disabled = not inter.is_any_items_in_prev_items()
        self.add_items_in_select()

        self.add_items(self.__looking_items_preset__)

    # Override method of base view class.
    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.owner.id != interaction.user.id:
            await interaction.response.send_message(f"Вы не можете взаимодейстовать с инвентарем пользователя `{self.owner}`.",
                                            ephemeral=True, delete_after=5)
            return False
        return True

    async def on_timeout(self) -> None:
        await self.original.delete()

    # Method triggers when user tap on button 'right'.
    async def __on_right_button_clicked__(self, interaction: Interaction):
        inter = self.interventory
        is_forward = True
        inter.on_switch_page(is_forward)
        self.__right_button__.disabled = not inter.is_any_items_in_next_items()
        self.__left_button__.disabled = not inter.is_any_items_in_prev_items()
        self.add_items_in_select()
        self.add_items(self.__looking_items_preset__)
        # Changed page property of class interventory
        await commands.cmd_inventory.on_switch_page_select(interaction, self, inter)

    # Method triggers when user tap on button 'left'.
    async def __on_left_button_clicked__(self, interaction: Interaction):
        inter = self.interventory
        is_forward = False
        inter.on_switch_page(is_forward)
        self.__right_button__.disabled = not inter.is_any_items_in_next_items()
        self.__left_button__.disabled = not inter.is_any_items_in_prev_items()
        self.add_items_in_select()
        self.add_items(self.__looking_items_preset__)
        await commands.cmd_inventory.on_switch_page_select(interaction, self, inter)

    # Method triggers when user push on button 'close'. Deletes message.
    async def __on_close_button_clicked__(self, interaction: Interaction):
        await interaction.response.defer()
        message_id = interaction.message.webhook_id
        if message_id is not None:
            await self.original.delete()

    # This method triggers when user pushed on button 'trade'.
    async def __on_trade_clicked__(self, interaction: Interaction):
        inter = self.interventory
        await commands.cmd_inventory.show_trade_inventory(interaction, self)

        pass

    # This method triggers when user push on button 'use'.
    async def __on_use_button_clicked__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        slot = inter.stack_store[i]
        item = slot[0]
        if item.stackable:
            self.check_items_count(len(slot))
            self.__x1__.callback = self.__on_use_1x__
            self.__x10__.callback = self.__on_use_10x__
            self.__back_button__.callback = self.__on_back_in_select_item_stage__
            self.add_items(self.__using_item_preset__)
            await commands.cmd_inventory.switch_view(interaction, self)
        else:
            await self.__on_use_1x__(interaction)

    async def __on_drop_button_clicked__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        slot = inter.stack_store[i]
        item = slot[0]
        if item.stackable:
            self.check_items_count(len(slot))
            self.__x1__.callback = self.__on_drop_1x__
            self.__x10__.callback = self.__on_drop_10x__
            self.__All__.callback = self.__on_drop_all__
            self.__back_button__.callback = self.__on_back_in_select_item_stage__
            self.add_items(self.__interactive_with_items_preset__)
            await commands.cmd_inventory.switch_view(interaction, self)
        else:
            await self.__on_drop_1x__(interaction)

    # Method triggers when user selected options.
    async def __on_selected_item__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        self.add_items(self.__choose_item_preset__)
        self.__back_button__.callback = self.__on_back_in_select_action_stage
        await commands.cmd_inventory.draw_inventory_edit(interaction, inter.stack_store, self, i)

    async def __on_back_in_select_item_stage__(self, interaction: Interaction):
        self.add_items(self.__choose_item_preset__)
        self.__back_button__.callback = self.__on_back_in_select_action_stage
        await commands.cmd_inventory.switch_view(interaction, self)

    async def __on_back_in_select_action_stage(self, interaction: Interaction):
        inter = self.interventory
        self.add_items(self.__looking_items_preset__)
        await commands.cmd_inventory.draw_inventory_edit(interaction, inter.stack_store, self)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_use_1x__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        chosen_slot = inter.stack_store[i]
        chosen_item = chosen_slot[0]
        if chosen_item.usable:
            await chosen_item.use(interaction, [chosen_item])
            await commands.cmd_inventory.show_inventory(interaction, is_private=True, inter_history=inter.inter_history)
            await interaction.channel.send(
                f"{chosen_item.name} успешно использован игроком {interaction.user}.", delete_after=5)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_use_10x__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        count_to_use = 10
        chosen_slot = inter.stack_store[i]
        if len(chosen_slot) >= count_to_use:
            chosen_items = chosen_slot[:count_to_use]
            if chosen_items[0].usable:
                await chosen_items[0].use(interaction, chosen_items)
                await commands.cmd_inventory.show_inventory(interaction, is_private=True,
                                                            inter_history=inter.inter_history)
                await interaction.channel.send(
                    f"{chosen_items[0].name} успешно использован игроком {interaction.user}.", delete_after=5)
        else:
            return await interaction.channel.send("В инвентаре не хватает предметов.", delete_after=5)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_drop_1x__(self, interaction: Interaction):
        await interaction.response.defer()
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        chosen_slot = inter.stack_store[i]
        chosen_item = chosen_slot[0]
        await commands.cmd_inventory.drop([chosen_item])
        await commands.cmd_inventory.show_inventory(interaction, is_private=True, inter_history=inter.inter_history)
        await interaction.channel.send(f"{chosen_item.name} выброшен из инвентаря {interaction.user}",
                                        delete_after=5)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_drop_10x__(self, interaction: Interaction):
        await interaction.response.defer()
        inter = self.interventory
        count_items = 10
        i = int(self.__select_item__.values[0])
        chosen_slot = inter.stack_store[i]
        chosen_10_x_items = chosen_slot[:count_items]
        await commands.cmd_inventory.drop(chosen_10_x_items)
        await commands.cmd_inventory.show_inventory(interaction, is_private=True, inter_history=inter.inter_history)
        await interaction.channel.send(f"`{count_items}` `{chosen_10_x_items[0].name}` "
                                       f"выброшен из инвентаря {interaction.user}",
                                       delete_after=5)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_drop_all__(self, interaction: Interaction):
        await interaction.response.defer()
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        chosen_slot = inter.stack_store[i]
        count_items = len(chosen_slot)
        await commands.cmd_inventory.drop(chosen_slot)
        await commands.cmd_inventory.show_inventory(interaction, is_private=True, inter_history=inter.inter_history)
        await interaction.channel.send(f"`{count_items}` `{chosen_slot[0].name}` "
                                       f"выброшен из инвентаря {interaction.user}",
                                       delete_after=5)

    def check_items_count(self, items_count):
        self.__x10__.disabled = not items_count >= 10
        self.__All__.disabled = not items_count >= 2

    def add_items(self, items: []):
        self.clear_items()
        for item in items:
            if item.custom_id == "Select":
                if len(item.options) == 0:
                    continue
            self.add_item(item)

    def add_items_in_select(self):
        inter = self.interventory
        self.__select_item__.options.clear()
        print(len(inter.stack_store))
        if len(inter.stack_store) > 0:
            for i in range(len(inter.stack_store)):
                list_items = inter.stack_store[i]
                self.__select_item__.add_option(label=list_items[0].name, value=str(i))


class OptionsNotFound(Exception):
    def __init__(self):
        super().__init__()
        self.text = f"Select have no items."
