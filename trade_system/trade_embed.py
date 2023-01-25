import discord
from utilities.emojis import Emoji


class Trade_Embed(discord.Embed):
    def __init__(self, trade):
        super().__init__()
        self.owner = trade.owner
        self.id = trade.id
        self.money = trade.cost
        self.timer = trade.timer
        self.title = f"⎢Трейд №`{self.id}`\n⎢Стоимость: `{self.money}` {Emoji.Primogem}"
        self.description = f"Данный трейд истечёт через `{self.timer // 60}` минут(ы)."
        self.set_author(name=self.owner, icon_url=self.owner.avatar)
