import json
import discord
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

class Trade_GUI():
    def __init__(self):
        with open('gui/trade_settings.json', 'r') as file:
            self.cfg = json.loads(file.read())
        cfg = self.cfg
        path = cfg['font_path']
        self.font = ImageFont.truetype(path, cfg['font_big_size'])
        self.medium_font = ImageFont.truetype(path, cfg['font_medium_size'])
        self.small_font = ImageFont.truetype(path, cfg['font_small_size'])
        self.mode = cfg['mode']
        self.portret_size = cfg['portret_size_k']
        self.portret_paddings_k = cfg['portret_paddings_k']
        self.backgrounds_path = cfg['backgrounds_path']
        self.background_size = cfg['background_size']
        self.format_file = cfg['format_file_bg']
        self.text_fill = cfg['text_fill']
        self.dict_rarity = cfg["rarity"]

        self.money_text_paddings_k = cfg['money_text_paddings_k']

        # Trade
        self.panel_item_holders_size_k = self.cfg["panel_item_holders_size_k"]
        self.panel_item_holders_paddings_k = self.cfg["panel_item_holders_paddings_k"]
        self.panel_items_size = self.cfg["panel_items_size"]
        self.panel_interval_btw_holders_k = self.cfg["panel_interval_btw_holders_k"]

    def draw(self, user: discord.User, items: [], money, profile_bytes: BytesIO) -> BytesIO:
        profile_bytes = Image.open(profile_bytes).convert(self.mode)
        im = Image.new(self.mode, self.background_size)

        (width, height) = im.size

        portret = make_portret(profile_bytes, self.portret_size)

        # Создание кисти
        im_draw = ImageDraw.Draw(im)

        im_draw.text((width * self.money_text_paddings_k[0], height * self.money_text_paddings_k[1]), str(money),
                     fill=(255, 255, 255), font=self.font, align="center", )

        im_draw.text((width * self.money_text_paddings_k[0] + 100, height * self.money_text_paddings_k[1]), str(user),
                     fill=(255, 255, 255), font=self.font, align="center", )

        if items is not None:
            n = len(items)
            interval = int(self.panel_interval_btw_holders_k * width)
            holder_len = int(self.panel_item_holders_size_k * height)
            indent_w = (width - (n * holder_len + (n - 1) * interval)) // 2
            for i in range(self.panel_items_size):
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
                else:
                    item_holder = Image.open(str(self.dict_rarity["default"])).convert(self.mode)

                    item_holder = item_holder.resize(
                        (int(height * self.panel_item_holders_size_k),
                         int(height * self.panel_item_holders_size_k)))

                im.paste(item_holder, (int(indent_w), int(height * self.panel_item_holders_paddings_k[1])), item_holder)
                indent_w += item_holder.width + self.panel_interval_btw_holders_k * width

        # Наложение изображения профиля на баннер.
        im.paste(im=portret, box=(int(self.portret_paddings_k[0] * width), int(self.portret_paddings_k[1] * height)),
                 mask=portret)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        return buffer


def prepare_mask(size, antialias=2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)

# Обрезает и масштабирует изображение под заданный размер.
# Вообще, немногим отличается от .thumbnail, но по крайней мере
# у меня результат получается куда лучше.
def crop(im, s: tuple):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0:
        im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0:
        im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)

def make_portret(image: BytesIO, size: tuple):
    portret = crop(image, size)
    portret.putalpha(prepare_mask(size, 4))
    return portret