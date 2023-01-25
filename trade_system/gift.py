import discord
import aiohttp
from io import BytesIO
from bot_ui_kit.ui_gift_interaction import UI_GiftView
from gui.gift_gui import Gift_GUI
from trade_system.gift_embed import GiftEmbed


class Gift:
    id: int = 0
    minute = 60

    def __init__(self, owner_user: discord.User, guild: discord.Guild, recipient: discord.User, items: {}, timer: int = None):
        Gift.id += 1
        self.id = Gift.id
        self.owner: discord.User = owner_user
        self.guild = guild
        self.recipient = recipient
        self.items = items
        if timer is None:
            self.timer = 5 * Gift.minute
        else:
            self.timer = timer * Gift.minute

    async def send(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.recipient.avatar}?size=512') as resp:
                profile_bytes = await resp.read()

        buffer = Gift_GUI().draw(self.owner, self.items, BytesIO(profile_bytes))
        file = discord.File(fp=buffer, filename="gift.png")
        embed = GiftEmbed(self)
        embed.set_image(url="attachment://gift.png")

        view = UI_GiftView(self)

        msg = await self.recipient.send(file=file, embed=embed, view=view)
        view.sourced_msg = msg
        return

