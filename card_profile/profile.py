from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json


class Profile:
    def __init__(self, size: () = None) -> None:
        with open('card_profile/settings.json', 'r') as file:
            self.cfg = json.loads(file.read())
        cfg = self.cfg

        self.background_size = cfg['background_size']
        if size:
            self.background_size = size
        self.backgrounds_path = cfg['backgrounds_path']
        self.path = cfg['font_path']
        self.font = ImageFont.truetype(self.path, cfg['font_big_size'])
        self.medium_font = ImageFont.truetype(self.path, cfg['font_medium_size'])
        self.small_font = ImageFont.truetype(self.path, cfg['font_small_size'])
        self.portret_size_k = cfg['portret_size_k']
        self.portret_size = (int(self.portret_size_k[0] * self.background_size[0]),
                             int(self.portret_size_k[0] * self.background_size[0]))
        self.portret_paddings_k = cfg['portret_paddings_k']
        self.portret_paddings = (int(self.background_size[0] * self.portret_paddings_k[0]),
                                 int(self.background_size[1] * self.portret_paddings_k[1]))
        self.vision_padding_k = cfg['vision_padding_k']
        self.vision_size_k = cfg["vision_size_k"]
        self.vision_size = (int(self.background_size[0] * self.vision_size_k[0]),
                            int(self.background_size[0] * self.vision_size_k[1]))
        self.mode = cfg['mode']

        self.mask_path = cfg['mask_path']
        self.format_file = cfg['format_file_bg']
        self.text_fill = cfg['text_fill']
        self.visions_source_path = cfg['visions_source_path']

        # Stats panel.
        self.inactive_opacity = cfg['inactive_opacity']
        self.active_opacity = cfg['active_opacity']

        self.premium_paddings_k = cfg['premium_paddings_k']
        self.premium_paddings = (int(self.premium_paddings_k[0] * self.background_size[0]),
                                 int(self.premium_paddings_k[1] * self.background_size[1]))
        self.premium_size_k = cfg['premium_size_k']
        self.premium_size = (int(self.premium_size_k[0] * self.background_size[1]),
                             int(self.premium_size_k[1] * self.background_size[1]))

        self.hoyolab_paddings = (int(self.premium_paddings[0] + self.background_size[0] * 0.1), self.premium_paddings[1])
        self.hoyolab_size = self.premium_size
        self.hoyolab_img_path = cfg['hoyolab_img_path']
        self.premium_img_path = cfg['premium_img_path']

    async def draw_content(self, im: Image, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO,
                           vision: str = None, premium: int = None, is_hoyolab: bool = False) -> Image:

        text_filling = (self.text_fill[0], self.text_fill[1], self.text_fill[2], self.text_fill[3])
        profile_bytes = Image.open(profile_bytes).convert(self.mode)
        premium_img = Image.open(self.premium_img_path).convert(self.mode)
        hoyolab_img = Image.open(self.hoyolab_img_path).convert(self.mode)
        im = im.resize((int(self.background_size[0]), int(self.background_size[1])))

        mask = Image.open(self.mask_path).convert(self.mode)


        # Размерим
        (width, height) = im.size
        resized_mask = mask.resize((width, height))
        (m_width, m_height) = resized_mask.size
        resized_premium_img = premium_img.resize(self.premium_size)
        resized_hoyolab_img = hoyolab_img.resize(self.hoyolab_size)
        premium_mask = resized_premium_img.copy()
        hoyolab_mask = resized_hoyolab_img.copy()

        # Блюрим баннер
        # im = im.filter(ImageFilter.BLUR)

        # Сопоставление размера маски с размером баннера.
        # mask.resize(im.size)

        # Получаем размеры основного баннера

        # Создание портрета из изображения профиля.
        portret = make_portret(profile_bytes, self.portret_size)

        if premium:
            resized_premium_img.putalpha(self.active_opacity)
        else:
            resized_premium_img.putalpha(self.inactive_opacity)

        if is_hoyolab:
            resized_hoyolab_img.putalpha(self.active_opacity)
        else:
            resized_hoyolab_img.putalpha(self.inactive_opacity)

        resized_mask.paste(resized_premium_img,
                           self.premium_paddings, premium_mask)

        resized_mask.paste(resized_hoyolab_img,
                           self.hoyolab_paddings, hoyolab_mask)

        # Создание кисти
        m_draw = ImageDraw.Draw(resized_mask)

        # Наложение изображения профиля на баннер.
        resized_mask.paste(im=portret, box=self.portret_paddings,
                 mask=portret)

        # Наложение глаза бога
        if vision is not None:
            vision_path = self.visions_source_path + vision + self.format_file
            vision_img = Image.open(vision_path)
            vision_paddings_on_icon = (int(self.portret_paddings[0] - self.vision_size[0] // 2
                                           + self.portret_size[0] * self.vision_padding_k[0]),
                                       int(self.portret_paddings[1] - self.vision_size[1] // 2
                                           + self.portret_size[1] * self.vision_padding_k[1]))
            resized_vision_img = vision_img.resize(
                (int(self.vision_size_k[0] * width), int(self.vision_size_k[1] * width)))
            resized_mask.paste(resized_vision_img,
                               vision_paddings_on_icon,
                               resized_vision_img)

        xp_bar_rect = 17 / 96 * width, 178 / 240 * height, 47 / 72 * width, 194 / 240 * height
        xp_filled_bar_rect = 17 / 96 * width, 178 / 240 * height, 17 / 96 * width * (
                    1 - xp / Profile.neededxp(rank)) + (
                                         xp / Profile.neededxp(rank) * 47 / 72 * width), 194 / 240 * height

        m_draw.text((int(30 / 108 * width), int(26 / 120 * height)), user, font=self.medium_font, fill=text_filling)

        uid_text = f'UID{uid}'
        uid_pos = (int(55 / 576 * width), int(276 / 480 * height))
        m_draw.text(uid_pos, uid_text, font=self.small_font, fill=text_filling)

        m_draw.rounded_rectangle(xy=xp_bar_rect, radius=15, fill=(0, 0, 0, 100))
        m_draw.rounded_rectangle(xy=xp_filled_bar_rect, radius=15, fill=(165, 200, 98, 255), width=5)

        rank_text = f'{rank}'
        rank_text_label = f"Ранг: {rank_text}"
        m_draw.text((xp_bar_rect[0], xp_bar_rect[1]), rank_text_label, font=self.medium_font,
                    fill=text_filling, anchor="ld")

        needed_xp = self.neededxp(rank)
        xp_text = f'{xp}/{needed_xp}'
        xp_text_label = f"EXP {xp_text}"

        xp_text_pos_avg_y = xp_bar_rect[3] - (xp_bar_rect[3] - xp_bar_rect[1]) // 2
        xp_text_pos_avg_x = xp_bar_rect[2] - 5
        xp_text_pos = (xp_text_pos_avg_x, xp_text_pos_avg_y)
        m_draw.text(xp_text_pos, xp_text_label, font=self.small_font, fill=text_filling, anchor="rm")

        count_chars_on_row = 25
        bio = string_cuts_on_rows(bio, count_chars_on_row)
        bio_text_position = (int(31 / 108 * width), int(22 / 60 * height))
        m_draw.text(bio_text_position, bio, font=self.small_font, fill=text_filling, anchor="la", align="left")

        # Наложение маски на баннер
        im.paste(resized_mask, resized_mask)

        return im

    async def draw(self, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO, card: str,
             vision: str = None, premium: int = None, is_hoyolab: bool = False) -> Image:
        # Загрузка шаблонных изображений.

        bg_path = self.backgrounds_path + card
        im = Image.open(bg_path + "_Card.png").convert(self.mode)
        image = await self.draw_content(im=im, user=user, uid=uid, bio=bio, rank=rank, xp=xp, profile_bytes=profile_bytes,
                                 vision=vision, premium=premium, is_hoyolab=is_hoyolab)
        return image




    @staticmethod
    def neededxp(level: int) -> int:
        return 1000 + level * 1000


class Utilities:
    def __init__(self):
        self.profilecard = Profile()

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

def string_cuts_on_rows(string : str, count_chars_in_row : int) -> str:
    length = len(string)
    if length < count_chars_in_row:
        return string
    counter = 0
    extra_length = count_chars_in_row // 5
    for i in range(length):
        counter += 1
        if string[i] == ' ' and counter >= count_chars_in_row:
            string = string[:i] + '\n' + string[i:]
            counter = 0
        elif counter - extra_length == count_chars_in_row:
            for j in range(len(string[i - 3 * extra_length:i - extra_length])):
                if string[j] == ' ':
                    string = string[:j] + '\n' + string[j:]
                    counter = 0
                    break
        elif counter - extra_length > count_chars_in_row:
            string = string[:i] + '\n' + string[i:]
            counter = 0
    return string