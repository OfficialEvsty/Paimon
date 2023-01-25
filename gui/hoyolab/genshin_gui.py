import json
import discord
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class Genshin_GUI:
    def __init__(self):
        with open("gui/genshin_settings.json", "r") as file:
            self.cfg = json.loads(file.read())
        self.bg_size = self.cfg["bg_size"]
        self.mode = self.cfg["mode"]

    def draw(self) -> BytesIO:
        color = (255, 255, 255, 255)
        im = Image.new(mode=self.mode, size=(self.bg_size[0], self.bg_size[1]), color=color)

        buffer = BytesIO()
        im.save(fp=buffer, format='png')
        buffer.seek(0)
        return buffer