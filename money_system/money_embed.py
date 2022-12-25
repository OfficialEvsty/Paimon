import discord
from io import BytesIO
from PIL import Image


class Money_Embed(discord.Embed):
    def __init__(self, user: discord.User, amount: int):
        super().__init__()
        self.money_icon_id = "<:Primogem:1055045588556730399>"
        self.title = f"Баланс: `{amount}` {self.money_icon_id}"
        self.set_author(name=user, icon_url=user.avatar)
        self.buffer = BytesIO()
        self.img = Image.open("item_system/item_images/Primogem.png")
        self.img.save(self.buffer, 'png')
        self.buffer.seek(0)
        self.file = discord.File(fp=self.buffer, filename="primogem.png")
        #self.set_thumbnail(url="attachment://primogem.png")