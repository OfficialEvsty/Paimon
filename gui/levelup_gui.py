from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json


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
        self.exp_img_path = cfg['exp_img_path']
        self.exp_img_size_k = cfg['exp_img_size_k']
        self.exp_img_paddings_k = cfg['exp_img_paddings_k']
        self.text_fill = cfg['text_fill']


    def draw(self, user: str, rank: int, profile_bytes: BytesIO) -> BytesIO:
        text_filling = (self.text_fill[0], self.text_fill[1], self.text_fill[2], self.text_fill[3])
        # Загрузка шаблонных изображений.

        im = Image.new(self.mode, size=(self.background_size[0], self.background_size[1]))
        profile_bytes = Image.open(profile_bytes).convert(self.mode)

        exp_sign = Image.open(self.exp_img_path).convert(self.mode)


        # Размерим
        (width, height) = im.size
        resized_exp_sign = exp_sign.resize((int(height * self.exp_img_size_k[0]), int(height * self.exp_img_size_k[1])))



        # Создание портрета из изображения профиля.
        portret = make_portret(profile_bytes, self.portret_size)

        # Создание кисти
        im_draw = ImageDraw.Draw(im)

        # Наложение изображения профиля на баннер.
        im.paste(im=portret, box=(int(self.portret_paddings_k[0] * width), int(self.portret_paddings_k[1] * height)), mask=portret)

        im.paste(resized_exp_sign, (int(width * self.exp_img_paddings_k[0]), int(height * self.exp_img_paddings_k[1])), resized_exp_sign)

        im_draw.text((int(41 / 108 * width), int(11 / 60 * height)), user, font=self.font, fill=text_filling)


        rank_text = f'{rank}'
        im_draw.text((int(96 / 108 * width), int(33 / 60 * height)), rank_text, font=self.font, fill=text_filling)

        rank_text_label = "Rank Up!"
        im_draw.text((int(40 / 108 * width), int(34 / 60 * height)), rank_text_label, font=self.medium_font,
                     fill=text_filling)

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
