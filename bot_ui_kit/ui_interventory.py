from discord.ui import View, Select, UserSelect, Modal, TextInput, Button, Item
from discord import ButtonStyle, TextStyle
from utilities.emojis import Emoji
from item_system.inventory_interaction import Interventory
from discord import Interaction, User
import commands

# This class provides interaction over inventory and user


class UI_InterventoryView(View):
    def __init__(self, user: User, interventory: Interventory):
        super(UI_InterventoryView, self).__init__()
        self.owner = user
        self.interventory = interventory

        self.__select_item__: Select = Select(placeholder="Select an item")
        self.__select_item__.callback = self.__on_selected_item__

        self.__select_user__: UserSelect = UserSelect(placeholder="Select an user")

        self.__right_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Right_Arrow)
        self.__right_button__.callback = self.__on_right_button_clicked__

        self.__left_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Left_Arrow)
        self.__left_button__.callback = self.__on_left_button_clicked__

        self.__use_button__ = Button(style=ButtonStyle.green, label="Use")
        self.__use_button__.callback = self.__on_use_button_clicked__

        self.__trade_button__ = Button(style=ButtonStyle.green, label="Trade")

        self.__drop_button__ = Button(style=ButtonStyle.red, label="Drop")
        self.__drop_button__.callback = self.__on_drop_button_clicked__

        self.__back_button__ = Button(style=ButtonStyle.red, label="Back")

        self.__close_button__ = Button(style=ButtonStyle.red, label="Close")
        self.__close_button__.callback = self.__on_close_button_clicked__

        self.__x1__ = Button(style=ButtonStyle.gray, label="x1")
        self.__x10__ = Button(style=ButtonStyle.gray, label="x10")
        self.__All__ = Button(style=ButtonStyle.gray, label="All")

        self.__apply_trade__ = Button(style=ButtonStyle.green, label="Apply")
        self.__give_to_user__ = Button(style=ButtonStyle.green, label="Give")

        self.__looking_items_preset__ = [self.__left_button__, self.__trade_button__, self.__close_button__,
                                     self.__right_button__, self.__select_item__]
        self.__choose_item_preset__ = [self.__left_button__, self.__use_button__, self.__drop_button__,
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

    # Method triggers when user tap on button 'right'.
    async def __on_right_button_clicked__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            inter = self.interventory
            is_forward = True
            inter.put_items_in_stack(is_forward)
            self.__right_button__.disabled = not inter.is_any_items_in_next_items()
            self.__left_button__.disabled = not inter.is_any_items_in_prev_items()
            self.add_items(self.__looking_items_preset__)
            self.add_items_in_select()
            await commands.cmd_inventory.on_switch_page_select(interaction, self, inter)

    # Method triggers when user tap on button 'left'.
    async def __on_left_button_clicked__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            inter = self.interventory
            is_forward = False
            inter.put_items_in_stack(is_forward)
            self.__right_button__.disabled = not inter.is_any_items_in_next_items()
            self.__left_button__.disabled = not inter.is_any_items_in_prev_items()
            self.add_items(self.__looking_items_preset__)
            self.add_items_in_select()
            await commands.cmd_inventory.on_switch_page_select(interaction, self, inter)

    # Method triggers when user push on button 'close'. Deletes message.
    async def __on_close_button_clicked__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            msg_id = interaction.message.id
            print("фак")
            if msg_id is not None:
                await interaction.followup.delete_message(msg_id)

    # This method triggers when user push on button 'use'.
    async def __on_use_button_clicked__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            inter = self.interventory
            i = int(self.__select_item__.values[0])
            slot = inter.stack_store[i]
            item = slot[0]
            if item.stackable:
                self.check_items_count(len(slot))
                self.__x1__.callback = self.__on_use_1x__
                self.__back_button__.callback = self.__on_back_in_select_item_stage__
                self.add_items(self.__interactive_with_items_preset__)
                await commands.cmd_inventory.switch_view(interaction, self)
            else:
                await self.__on_use_1x__(interaction)

    async def __on_drop_button_clicked__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            inter = self.interventory
            i = int(self.__select_item__.values[0])
            slot = inter.stack_store[i]
            item = slot[0]
            if item.stackable:
                self.check_items_count(len(slot))
                self.__x1__.callback = self.__on_drop_1x__
                self.__back_button__.callback = self.__on_back_in_select_item_stage__
                self.add_items(self.__interactive_with_items_preset__)
                await commands.cmd_inventory.switch_view(interaction, self)
            else:
                await self.__on_drop_1x__(interaction)

    # Method triggers when user selected options.
    async def __on_selected_item__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            inter = self.interventory
            i = int(self.__select_item__.values[0])
            self.add_items(self.__choose_item_preset__)
            self.__back_button__.callback = self.__on_back_in_select_action_stage
            await commands.cmd_inventory.draw_inventory_edit(interaction, inter.stack_store, i, self)

    async def __on_back_in_select_item_stage__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            self.add_items(self.__choose_item_preset__)
            self.__back_button__.callback = self.__on_back_in_select_action_stage
            await commands.cmd_inventory.switch_view(interaction, self)

    async def __on_back_in_select_action_stage(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            self.add_items(self.__looking_items_preset__)
            await commands.cmd_inventory.switch_view(interaction, self)

    async def __on_use_1x__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            await interaction.response.defer()
            inter = self.interventory
            i = int(self.__select_item__.values[0])
            chosen_slot = inter.stack_store[i]
            chosen_item = chosen_slot[0]
            if chosen_item.usable:
                await chosen_item.use(interaction, chosen_item)
                await interaction.channel.send(
                    f"{chosen_item.name} успешно использован игроком {interaction.user}.", delete_after=5)

    async def __on_drop_1x__(self, interaction: Interaction):
        if self.owner.id == interaction.user.id:
            await interaction.response.defer()
            inter = self.interventory
            i = int(self.__select_item__.values[0])
            chosen_slot = inter.stack_store[i]
            chosen_item = chosen_slot[0]
            await commands.cmd_inventory.drop(interaction, chosen_item)
            await commands.cmd_inventory.show_inventory(interaction, is_private=True)
            await interaction.channel.send(f"{chosen_item.name} выброшен из инвентаря {interaction.user}",
                                            delete_after=5)








    def check_items_count(self, items_count):
        self.__x10__.disabled = not items_count >= 10
        self.__All__.disabled = not items_count >= 2

    def add_items(self, items: []):
        self.clear_items()
        for item in items:
            self.add_item(item)

    def add_items_in_select(self):
        inter = self.interventory
        self.__select_item__.options.clear()
        print(len(inter.stack_store))
        if len(inter.stack_store) > 0:
            for i in range(len(inter.stack_store)):
                list_items = inter.stack_store[i]
                self.__select_item__.add_option(label=list_items[0].name, value=str(i))
        else:
            self.__select_item__.disabled = True

