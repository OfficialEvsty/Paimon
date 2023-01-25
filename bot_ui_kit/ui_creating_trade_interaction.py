from discord.ui import View, Select, Button, UserSelect
from discord import ButtonStyle, User, Webhook, Interaction
from item_system.interventory import Interventory
from utilities.emojis import Emoji
from bot_ui_kit.support_entities.listening_blocker_button import ListeningBlocker
import commands


class UI_CreatingTradeView(View):
    def __init__(self, user: User, interventory: Interventory):
        super().__init__()
        self.owner = user
        self.interventory = interventory
        self.original: Webhook = None

        self.__select_item__: Select = Select(placeholder="Select an item", custom_id="Select")
        self.__select_item__.callback = self.__on_selected_item__

        self.__select_user__: UserSelect = UserSelect(placeholder="Select an user to give items")
        self.__select_user__.callback = self.__on_user_selected__

        self.__right_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Right_Arrow)
        self.__right_button__.callback = self.__on_right_button_clicked__

        self.__left_button__ = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Left_Arrow)
        self.__left_button__.callback = self.__on_left_button_clicked__

        self.__right_button_end__ = Button(style=ButtonStyle.gray, disabled=True, label=">>")

        self.__left_button_begin__ = Button(style=ButtonStyle.gray, disabled=True, label="<<")

        self.__create_trade_button__ = Button(style=ButtonStyle.green, label="Create", disabled=True)
        self.__create_trade_button__.callback = self.__shift_create_trade__

        self.__market_button__ = Button(style=ButtonStyle.green, label="Market", disabled=True)

        self.__give_user__ = Button(style=ButtonStyle.green, label="Give", disabled=True)
        self.__give_user__.callback = self.__on_give_user_clicked

        self.__back_button__ = Button(style=ButtonStyle.red, label="Back")

        self.__close_button__ = Button(style=ButtonStyle.red, label="Close")
        self.__close_button__.callback = self.__on_close_button_clicked__

        self.__x1__ = Button(style=ButtonStyle.gray, label="x1")
        self.__x1__.callback = self.__1x__

        self.__x10__ = Button(style=ButtonStyle.gray, label="x10")
        self.__x10__.callback = self.__10x__

        self.__All__ = Button(style=ButtonStyle.gray, label="All")
        self.__All__.callback = self.__all__

        self.__looking_items_preset__ = [self.__left_button__, self.__create_trade_button__, self.__close_button__,
                                     self.__right_button__, self.__select_item__]
        self.__interactive_with_items_preset__ = [self.__left_button__, self.__x1__, self.__x10__, self.__All__,
                                                  self.__right_button__, self.__left_button_begin__,
                                                  self.__create_trade_button__, self.__back_button__,
                                                  self.__right_button_end__, self.__select_item__]
        self.__choose_trade_way__ = [self.__left_button__, self.__give_user__, self.__market_button__,
                                     self.__close_button__,
                                     self.__right_button__, self.__select_user__]

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
            await interaction.response.send_message(
                f"Вы не можете взаимодейстовать с инвентарем пользователя `{self.owner}`.",
                ephemeral=True, delete_after=5)
            return False
        return True

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

    async def __shift_create_trade__(self, interaction: Interaction):
        self.add_items(self.__choose_trade_way__)
        await commands.cmd_inventory.switch_view(interaction, self)

    # Method triggers when user push on button 'close'. Deletes message.
    async def __on_close_button_clicked__(self, interaction: Interaction):
        await interaction.response.defer()
        message_id = interaction.message.webhook_id
        if message_id is not None:
            await self.original.delete()

    # Method triggers when user selected options.
    async def __on_selected_item__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        items = inter.stack_store[i]
        if not items[0].stackable:
            await self.__1x__(interaction)
        else:
            count = len(items)
            self.check_items_count(count)
            self.add_items(self.__interactive_with_items_preset__)
            self.__back_button__.callback = self.__on_back_in_select_action_stage
            await commands.cmd_inventory.show_trade_inventory(interaction, self, interventory=inter, chosen_item=i)

    async def __on_user_selected__(self, interaction: Interaction):
        self.__give_user__.disabled = False
        self.add_items(self.__choose_trade_way__)
        await commands.cmd_inventory.switch_view(interaction, self)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_give_user_clicked(self, interaction: Interaction):
        if len(self.__select_user__.values) > 0:
            chosen_user = self.__select_user__.values[0]
            if chosen_user is not None:
                await commands.cmd_inventory.gift(interaction, self.interventory, chosen_user)
        else:
            return await interaction.response.send_message("Сначала выберите пользователя, которому хотите подарить предметы.",
                                                        ephemeral=True, delete_after=5)
        await commands.cmd_inventory.show_inventory(interaction, is_private=True)


    async def __on_market__(self, interaction: Interaction):
        await commands.cmd_inventory.trade(interaction, self.interventory, )

    # Method triggers on user's click. Adding items in trade list.
    @ListeningBlocker.add_to_listening_blocker
    async def __1x__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        item = inter.stack_store[i][0]
        inter.add_items_in_trade([item])
        self.add_items_in_select()
        self.add_items(self.__looking_items_preset__)
        if len(inter.trade_items) > 0:
            self.__create_trade_button__.disabled = False
        await commands.cmd_inventory.show_trade_inventory(interaction, self, inter)


    # Method triggers on user's click. Adding items in trade list.
    @ListeningBlocker.add_to_listening_blocker
    async def __10x__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        items = inter.stack_store[i]
        count = 10
        if len(items) >= 10:
            items_to_trade = items[:count]
            inter.add_items_in_trade(items_to_trade)
            self.add_items_in_select()
            self.add_items(self.__looking_items_preset__)
            if len(inter.trade_items) > 0:
                self.__create_trade_button__.disabled = False
            await commands.cmd_inventory.show_trade_inventory(interaction, self, inter)

    @ListeningBlocker.add_to_listening_blocker
    async def __all__(self, interaction: Interaction):
        inter = self.interventory
        i = int(self.__select_item__.values[0])
        items = inter.stack_store[i]
        items_to_trade = items
        inter.add_items_in_trade(items_to_trade)
        self.add_items_in_select()
        self.add_items(self.__looking_items_preset__)
        if len(inter.trade_items) > 0:
            self.__create_trade_button__.disabled = False
        await commands.cmd_inventory.show_trade_inventory(interaction, self, inter)

    async def __on_back_in_select_item_stage__(self, interaction: Interaction):
        self.add_items(self.__choose_item_preset__)
        self.__back_button__.callback = self.__on_back_in_select_action_stage
        await commands.cmd_inventory.switch_view(interaction, self)

    async def __on_back_in_select_action_stage(self, interaction: Interaction):
        inter = self.interventory
        self.add_items(self.__looking_items_preset__)
        await commands.cmd_inventory.draw_inventory_edit(interaction, inter.stack_store, self)

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