import discord
import aiohttp
from io import BytesIO
from bot_ui_kit.ui_trade_interaction import UI_Trade_View
from gui.trade_gui import Trade_GUI
from commands.cmd_guild_settings import get_notifications_channel


class Trade:
    id: int = 0

    def __init__(self, owner_user: discord.User, items: [], money: int, timer: int = None):

        Trade.id += 1
        self.id = Trade.id
        self.owner: discord.User = owner_user
        self.items = items
        self.cost: int = money
        if timer is None:
            self.timer = 180
        self.timer = timer
        self.is_purchased = False

    async def create_trade(self, interaction: discord.Interaction):
        user = interaction.user

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{user.avatar}?size=512') as resp:
                profile_bytes = await resp.read()

        buffer = Trade_GUI().draw(user, self.items, self.cost, BytesIO(profile_bytes))
        file = discord.File(fp=buffer, filename="trade.png")

        if self.timer is not None:
            ui_trade = UI_Trade_View(self)
        else:
            ui_trade = UI_Trade_View(self)
        view: UI_Trade_View = await ui_trade.create_buttons()

        channel_to_send_notification = await get_notifications_channel(interaction.guild)

        if channel_to_send_notification is not None:
            msg = await channel_to_send_notification.send(file=file, view=view)
        else:
            msg = await interaction.channel.send(file=file, view=view)
        view.sourced_msg = msg

