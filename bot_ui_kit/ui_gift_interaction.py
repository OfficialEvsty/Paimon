import discord
from discord import ButtonStyle, Interaction
from discord.ui import Button, View
from item_system.inventory import Inventory
from utilities.emojis import Emoji
from transaction_system.transaction import Transaction
from bot_ui_kit.support_entities.listening_blocker_button import ListeningBlocker


class UI_GiftView(View):
    def __init__(self, gift):
        super().__init__(timeout=gift.timer)
        self.gift = gift
        self.on_timeout = self.on_timeout
        self.owner_id = gift.owner.id
        self.is_accepted: bool = False
        self.sourced_msg: discord.Message = None

        self.__accept_button__ = Button(style=ButtonStyle.green, emoji=Emoji.Accept_Mark)
        self.__accept_button__.callback = self.__on_accept__

        self.__revert_button__ = Button(style=ButtonStyle.red, emoji=Emoji.Revert_Mark)
        self.__revert_button__.callback = self.__on_revert__

        self.__interaction_preset__ = [self.__accept_button__, self.__revert_button__]

        self.construct()

    def add_items(self, items: []):
        self.clear_items()
        for item in items:
            if item.custom_id == "Select":
                if len(item.options) == 0:
                    continue
            self.add_item(item)

    def construct(self):
        self.add_items(self.__interaction_preset__)

    async def on_timeout(self):
        if self.is_accepted is False:
            list_items = self.dict_to_list_items()
            await Inventory.draw_items_in_inventory(self.gift.owner, list_items)
            await self.sourced_msg.delete()

    @ListeningBlocker.add_to_listening_blocker
    async def __on_accept__(self, interaction: Interaction):
        user = interaction.user
        member = await self.gift.guild.fetch_member(user.id)
        owner_member = await self.gift.guild.fetch_member(self.gift.owner.id)
        list_items = self.dict_to_list_items()
        await Inventory.draw_items_in_inventory(user, list_items)
        msg = interaction.message
        self.is_accepted = True
        if msg:
            await msg.delete()
            await interaction.response.send_message(f"Вы успешно приняли подарок пользователя {self.gift.owner}.",
                                                    delete_after=5)
            gift_accepted_notification = f"Ваш подарок был принят пользователем {user}."
            recipient_transaction = Transaction(member, reason=f"Принят подарок от пользователя {self.gift.owner}.",
                                                received_items=self.gift.items)
            await recipient_transaction.send()

            donor_transaction = Transaction(owner_member, reason=f"Подарил подарок пользователю {user}.",
                                            given_items=self.gift.items)

            await donor_transaction.send()

            await self.gift.owner.send(gift_accepted_notification, delete_after=5)

    @ListeningBlocker.add_to_listening_blocker
    async def __on_revert__(self, interaction: Interaction):
        list_items = self.dict_to_list_items()
        await Inventory.draw_items_in_inventory(self.gift.owner, list_items)
        msg = interaction.message
        self.is_accepted = False
        if msg:
            await msg.delete()
            await interaction.response.send_message(f"Вы отклонили подарок пользователя {self.gift.owner}.",
                                                    delete_after=5)
            gift_reverted_notification = f"Ваш подарок был отклонен пользователем {self.gift.owner}."

            await self.gift.owner.send(gift_reverted_notification, delete_after=5)

    def dict_to_list_items(self) -> []:
        list_items = []
        for slot in self.gift.items.values():
            for item in slot:
                list_items.append(item)
        return list_items
