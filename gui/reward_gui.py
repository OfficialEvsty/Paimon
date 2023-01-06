import json
import discord
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

class Reward_GUI():
    def __init__(self):
        with open('gui/reward_settings.json', 'r') as file:
            self.cfg = json.loads(file.read())
        cfg = self.cfg
        path = cfg['font_path']
        self.font = ImageFont.truetype(path, cfg['font_big_size'])
        self.medium_font = ImageFont.truetype(path, cfg['font_medium_size'])
        self.small_font = ImageFont.truetype(path, cfg['font_small_size'])
        self.mode = cfg['mode']
        self.background_path = cfg['background_path']
        self.background_size = cfg['background_size']
        self.format_file = cfg['format_file_bg']
        self.text_fill = cfg['text_fill']
        self.dict_rarity = cfg["rarity"]

        self.money_text_paddings_k = cfg['money_text_paddings_k']


        self.panel_item_holders_size_k = self.cfg["panel_item_holders_size_k"]
        self.panel_item_holders_paddings_k = self.cfg["panel_item_holders_paddings_k"]
        self.panel_items_size = self.cfg["panel_items_size"]
        self.panel_interval_btw_holders_k = self.cfg["panel_interval_btw_holders_k"]

    def draw(self, user: discord.User, items: [], money) -> BytesIO:
        im = Image.open(self.background_path)
        """back = Image.open("utilities/images/back.jpg").convert(self.mode)
        back = back.resize(im.size)"""


        (width, height) = im.size

        if money:
            length = 1
        else:
            length = 0

        if items is not None:
            n = len(items)
            interval = int(self.panel_interval_btw_holders_k * width)
            holder_len = int(self.panel_item_holders_size_k * height)
            indent_w = (width - ((n + length) * holder_len + (n + length - 1) * interval)) // 2
        elif length != 0:
            interval = int(self.panel_interval_btw_holders_k * width)
            holder_len = int(self.panel_item_holders_size_k * height)
            indent_w = (width - ((length) * holder_len + (length - 1) * interval)) // 2
            n = 0
        else:
            return
        print(n, length)
        for i in range(n + length):
            if i < n:
                item_holder = Image.open(str(self.dict_rarity[items[i].rarity]))

                item_holder = item_holder.resize(
                    (int(height * self.panel_item_holders_size_k), int(height * self.panel_item_holders_size_k)))


                item_img = Image.open(items[i].img_url)
                resized_item_img = item_img.resize(
                    (int(item_holder.width), int(item_holder.width)))
                mask = resized_item_img.copy()
                resized_item_img.putalpha(255)

                item_holder.paste(im=resized_item_img, mask=mask)
                im.paste(item_holder, (int(indent_w), int(height * self.panel_item_holders_paddings_k[1])), item_holder)
                indent_w += item_holder.width + self.panel_interval_btw_holders_k * width
            else:
                item_holder = Image.open(str(self.dict_rarity["special"]))

                item_holder = item_holder.resize(
                    (int(height * self.panel_item_holders_size_k), int(height * self.panel_item_holders_size_k)))

                item_img = Image.open("item_system/item_images/Primogem.png")
                resized_item_img = item_img.resize(
                    (int(item_holder.width), int(item_holder.width)))
                mask = resized_item_img.copy()
                resized_item_img.putalpha(255)

                item_holder.paste(im=resized_item_img, mask=mask)
                im.paste(item_holder, (int(indent_w), int(height * self.panel_item_holders_paddings_k[1])), item_holder)
                indent_w += item_holder.width + self.panel_interval_btw_holders_k * width

        # Наложение изображения профиля на баннер
        #back.paste(im, mask=im)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        return buffer