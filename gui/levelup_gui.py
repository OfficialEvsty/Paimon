from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import random

class LevelUp_GUI:
    def __init__(self) -> None:
        with open('gui/levelup_settings.json', 'r') as file:
            self.cfg = json.loads(file.read())
        cfg = self.cfg
        path = cfg['font_path']
        self.font = ImageFont.truetype(path, cfg['font_big_size'])
        self.medium_font = ImageFont.truetype(path, cfg['font_medium_size'])
        self.small_font = ImageFont.truetype(path, cfg['font_small_size'])
        self.portret_size = cfg['portret_size_k']
        self.portret_paddings_k = cfg['portret_paddings_k']
        self.mode = cfg['mode']
        self.background_size = cfg['background_size']
        self.rank_up_img_path = cfg['rank_up_panel_img']
        self.rank_up_img_size_k = cfg['rank_up_img_size_k']
        self.rank_up_img_paddings_k = cfg['rank_up_img_paddings_k']
        self.text_fill = cfg['text_fill']
        self.bg_path = cfg['bg_path']
        self.bg_collection = cfg['backgrounds_collection']
        self.rank_up_img_path = cfg['rank_up_panel_img']
        self.rank_text_paddings_k = cfg['rank_text_paddings_k']
        self.rank_up_text_paddings_k = cfg['rank_up_text_paddings_k']


    def draw(self, user: str, rank: int, profile_bytes: BytesIO) -> BytesIO:
        text_filling = (self.text_fill[0], self.text_fill[1], self.text_fill[2], self.text_fill[3])
        # Загрузка шаблонных изображений.
        background_path = self.bg_collection["bg_" + str(random.randint(1, len(self.bg_collection)))]

        im = Image.open(background_path)

        profile_bytes = Image.open(profile_bytes).convert(self.mode)

        rank_up_img = Image.open(self.rank_up_img_path).convert(self.mode)


        # Размерим
        im = im.resize(size=(self.background_size[0], self.background_size[1]))
        (width, height) = im.size
        rank_up_img = rank_up_img.resize((int(rank_up_img.width * self.rank_up_img_size_k[0]), int(rank_up_img.height * self.rank_up_img_size_k[1])))



        # Создание портрета из изображения профиля.
        portret = make_portret(profile_bytes, self.portret_size)

        # Создание кисти
        im_draw = ImageDraw.Draw(im)
        rank_draw = ImageDraw.Draw(rank_up_img)

        # Наложение изображения профиля на баннер.
        im.paste(im=portret, box=(int(self.portret_paddings_k[0] * width), int(self.portret_paddings_k[1] * height)), mask=portret)

        im_draw.text((int(self.portret_paddings_k[0] * width + portret.width * 1.2),
                      int(self.portret_paddings_k[1] * height + portret.height // 3)), user, font=self.font,
                     fill=text_filling)


        rank_text = f'{rank}'
        rank_draw.text((int(rank_up_img.width * self.rank_text_paddings_k[0]),
                       int(rank_up_img.height * self.rank_text_paddings_k[1])), rank_text, font=self.font,
                       fill=text_filling, anchor="ms")

        rank_text_label = "Rank Up!"
        rank_draw.text((int(rank_up_img.width * self.rank_up_text_paddings_k[0]),
                        int(rank_up_img.height * self.rank_up_text_paddings_k[1])), rank_text_label,
                       font=self.font, fill=text_filling, anchor="ms")

        left_padding = (width - rank_up_img.width) // 2
        im.paste(rank_up_img,
                 (int(left_padding), int(height * self.rank_up_img_paddings_k[1])),
                 rank_up_img)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        return buffer

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

def prepare_mask(size, antialias=2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)
