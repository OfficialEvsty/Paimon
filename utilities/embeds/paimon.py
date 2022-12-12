import discord
import json
from bot import Bot

class Paimon_Embed:
    def __init__(self):
        with open("utilities/embeds/settings.json") as file:
            self.cfg = json.loads(file.read())
        self.cfg = self.cfg["paimon"]
        self.author: discord.Member = Bot.bot.user
        self.color = discord.Color.lighter_grey()

    def construct(self, title: str, description: str, image_url: str = None, footer_text: str = None,
                  tumbnail_url: str = None) -> discord.Embed:
        self.author_img = self.author.avatar
        embed = discord.Embed(
            title=title,
            description=description,
            color=self.color,
        ).set_author(
            name=self.author,
            icon_url=self.author_img
        ).set_image(
            url=image_url
        ).set_footer(
            text=footer_text
        ).set_thumbnail(
            url=tumbnail_url
        )

        return embed

