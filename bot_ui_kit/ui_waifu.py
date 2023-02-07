from discord import Webhook, ButtonStyle, Interaction
from discord.ui import View, Button
from utilities.emojis import Emoji
from waifu_system.harem_interaction import HaremInteraction
import commands.cmd_waifu


class UI_WaifuView(View):
    def __init__(self, inter: HaremInteraction, is_mine: bool = True):
        super(UI_WaifuView, self).__init__()
        self.inter = inter
        self.owner = inter.harem.owner
        self.harem = inter.harem
        self.original: Webhook = None

        self.is_mine = is_mine

        self.__right_button = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Right_Arrow)
        self.__right_button.callback = self.__on_right_button_clicked

        self.__left_button = Button(style=ButtonStyle.gray, disabled=True, emoji=Emoji.Left_Arrow)
        self.__left_button.callback = self.__on_left_button_clicked

        self.__harem_button = Button(style=ButtonStyle.green, disabled=True, label="Гарем")
        self.__harem_button.callback = self.__on_harem_button_clicked

        self.__gift_button = Button(style=ButtonStyle.green, label="Подарок")
        self.__gift_button.callback = self.__on_gift_button_clicked

        self.__info_button = Button(style=ButtonStyle.gray, label="Инфо")
        self.__info_button.callback = self.__on_info_clicked

        self.__improve_button = Button(style=ButtonStyle.green, label="Повысить")
        self.__improve_button.callback = self.__on_improve_button_clicked

        self.__claim_button = Button(style=ButtonStyle.green, label="Потребовать")
        self.__claim_button.callback = self.__on_claim_button_clicked

        self.__loving_button = Button(style=ButtonStyle.green, label="Признаться")
        self.__loving_button.callback = self.__on_loving_button_clicked

        self.__drop_button = Button(style=ButtonStyle.red, label="Выбросить")
        self.__drop_button.callback = self.__on_drop_button_clicked

        self.__back_button = Button(style=ButtonStyle.red, label="Назад")

        self.__close_button = Button(style=ButtonStyle.red, label="Закрыть")
        self.__close_button.callback = self.__on_close_button_clicked__

        self.__x1__ = Button(style=ButtonStyle.gray, label="x1")
        self.__x10__ = Button(style=ButtonStyle.gray, label="x10")

        self.__looking_waifus_preset = [self.__left_button, self.__gift_button, self.__loving_button, self.__info_button,
                                       self.__back_button, self.__close_button, self.__right_button]
        self.__looking_other_waifus_preset = [self.__left_button, self.__loving_button, self.__info_button,
                                       self.__back_button, self.__close_button, self.__right_button]
        self.__more_info_preset = [self.__left_button, self.__improve_button, self.__drop_button, self.__back_button,
                                         self.__close_button, self.__right_button]
        self.__another_waifu_preset = [self.__info_button, self.__claim_button, self.__loving_button, self.__harem_button, self.__close_button]
        self.__my_waifu_profile_preset = [self.__info_button, self.__harem_button, self.__close_button]
        self.prev_preset = None

        if is_mine:
            self.__construct_my_profile()
        else:
            self.__construct_another_profile()
        # self.__construct()  # Constructed a view with necessary interaction items for first preview.

    def __construct(self):
        harem_len = len(self.harem.waifus)
        self.__right_button.disabled = False if harem_len > 1 else True
        self.__left_button.disabled = False if harem_len > 1 else True

        self.__harem_button.disabled = False if harem_len > 0 else True

    def __construct_my_profile(self):
        self.__construct()
        self.add_items(self.__my_waifu_profile_preset)

        # Override method of base view class.

    def __construct_another_profile(self):
        self.__construct()
        self.add_items(self.__another_waifu_preset)

    """async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.owner.id != interaction.user.id:
            await interaction.response.send_message(
                f"Вы не можете взаимодейстовать с вайфу пользователя `{self.owner}`.",
                ephemeral=True, delete_after=5)
            return False
        return True"""

    async def __on_right_button_clicked(self, interaction: Interaction):
        is_forward = True
        self.inter.move(is_forward)
        self.inter.switch()
        if self.prev_preset is not None:
            self.clear_items()
            self.add_items(self.prev_preset)
        await commands.cmd_waifu.show_profile(interaction, self.inter, ui=self, member=self.owner)

    async def __on_left_button_clicked(self, interaction: Interaction):
        is_forward = False
        self.inter.move(is_forward)
        self.inter.switch()
        if self.prev_preset is not None:
            self.clear_items()
            self.add_items(self.prev_preset)
        await commands.cmd_waifu.show_profile(interaction, self.inter, ui=self, member=self.owner)

    async def __on_harem_button_clicked(self, interaction: Interaction):
        self.clear_items()
        if self.is_mine:
            self.add_items(self.__looking_waifus_preset)
            self.__back_button.callback = self.__on_back_to_my_owner_button_clicked
        else:
            self.add_items(self.__looking_other_waifus_preset)
            self.__back_button.callback = self.__on_back_to_other_owner_button_clicked
        self.inter.switch(index=0)
        await commands.cmd_waifu.show_profile(interaction, self.inter, self, member=self.owner, chosen_index=0)

    async def __on_improve_button_clicked(self, interaction: Interaction):
        await self.inter.chosen.upgrade_waifu_attributes(levels=1)
        await interaction.response.send_message(f"Вайфу {self.inter.chosen.member} повышена на {1} уровень.")

    async def __on_loving_button_clicked(self, interaction: Interaction):
        pass

    async def __on_drop_button_clicked(self, interaction: Interaction):
        pass

    async def __on_close_button_clicked__(self, interaction: Interaction):
        await interaction.response.defer()
        message_id = interaction.message.webhook_id
        if message_id is not None:
            await self.original.delete()

    async def __on_gift_button_clicked(self, interaction: Interaction):
        await self.inter.chosen.gift()
        await commands.cmd_waifu.show_profile(interaction)

    async def __on_claim_button_clicked(self, interaction: Interaction):
        member = await interaction.guild.fetch_member(interaction.user.id)
        await self.harem.add_waifu(member, self.owner)
        await interaction.response.send_message(f"Вайфу {self.owner} был добавлен в ваш Гарем.", ephemeral=True,
                                                delete_after=5)

    # Доработать
    async def __on_info_clicked(self, interaction: Interaction):
        self.prev_preset = self.children
        self.clear_items()
        self.add_items(self.__more_info_preset)
        await commands.cmd_waifu.show_profile(interaction, self.inter, self, info_mode=True, member=self.owner)

    async def __on_back_to_my_owner_button_clicked(self, interaction: Interaction):
        self.clear_items()
        self.add_items(self.__my_waifu_profile_preset)
        self.inter.choose_owner()
        await commands.cmd_waifu.show_profile(interaction, self.inter, self, member=self.owner)

    async def __on_back_to_other_owner_button_clicked(self, interaction: Interaction):
        self.clear_items()
        self.add_items(self.__another_waifu_preset)
        self.inter.choose_owner()
        await commands.cmd_waifu.show_profile(interaction, self.inter, self, member=self.owner)

    def add_items(self, items: []):
        self.clear_items()
        for item in items:
            self.add_item(item)



