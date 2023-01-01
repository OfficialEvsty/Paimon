import discord
from money_system.money import get_money_db, update_money_db
from item_system.inventory import Inventory
from utilities.emojis import Emoji
from transaction_system.transaction import Transaction



class UI_Trade_View(discord.ui.View):
    def __init__(self, trade):
        super().__init__(timeout=trade.timer)
        self.trade = trade
        self.on_timeout = None
        self.owner_id = trade.owner.id
        self.sourced_msg: discord.Message = None

    async def create_buttons(self) -> discord.ui.View:
        buy_button = discord.ui.Button(
            label="                         Buy                         ",
            style=discord.ButtonStyle.green
        )

        async def on_accept_trade(interaction: discord.Interaction):
            user = interaction.user
            user_id = user.id
            msg = interaction.message
            if user_id is not self.owner_id:
                user_current_money = await get_money_db(user, interaction.guild)
                if int(user_current_money) >= int(self.trade.cost):
                    await update_money_db(user, interaction.guild, -int(self.trade.cost))
                    await update_money_db(self.trade.owner, interaction.guild, self.trade.cost)
                    await Inventory.draw_items_in_inventory(user, self.trade.items)
                    self.is_purchased = True
                    if msg:
                        await msg.delete()
                        await interaction.response.send_message("Сделка успешно проведена.", delete_after=5)
                    notification_items_returned = f"Ваш трейд №`{self.trade.id}` был куплен пользователем `{interaction.user}` за `{self.trade.cost}` {Emoji.Primogem}."
                    transaction_purchaser = Transaction(user, reason=f"Покупка трейда №{self.trade.id}", money=-self.trade.cost,
                                                        received_items=self.trade.items)
                    await transaction_purchaser.send()
                    transaction_seller = Transaction(self.trade.owner, reason=f"Продажа трейда №{self.trade.id}",
                                                     money=self.trade.cost, given_items=self.trade.items)
                    await transaction_seller.send()


                    await self.trade.owner.send(notification_items_returned)
                else:
                    await interaction.response.send_message("У вас недостаточно средств для данной покупки.", delete_after=5, ephemeral=True)

        buy_button.callback = on_accept_trade

        async def on_timeout():
            if self.trade.is_purchased is False:
                await Inventory.draw_items_in_inventory(self.trade.owner, self.trade.items)
                if self.sourced_msg:
                    await self.sourced_msg.delete()
                notification_items_returned = f"Ваш трейд №`{self.trade.id}` истёк. Все ресурсы вернулись обратно в Ваш инвентарь."

                await self.trade.owner.send(notification_items_returned)


        self.on_timeout = on_timeout

        self.add_item(buy_button)
        return self
