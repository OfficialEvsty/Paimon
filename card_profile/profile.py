from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json


class Profile:
    def __init__(self) -> None:
        with open('card_profile/settings.json', 'r') as file:
            self.cfg = json.loads(file.read())
        cfg = self.cfg
        path = cfg['font_path']
        self.font = ImageFont.truetype(path, cfg['font_big_size'])
        self.medium_font = ImageFont.truetype(path, cfg['font_medium_size'])
        self.small_font = ImageFont.truetype(path, cfg['font_small_size'])
        self.portret_size = cfg['portret_size_k']
        self.portret_paddings_k = cfg['portret_paddings_k']
        self.vision_padding_k = cfg['vision_padding_k']
        self.vision_size_k = cfg["vision_size_k"]
        self.mode = cfg['mode']
        self.backgrounds_path = cfg['backgrounds_path']
        self.background_size = cfg['background_size']
        self.mask_path = cfg['mask_path']
        self.exp_img_path = cfg['exp_img_path']
        self.format_file = cfg['format_file_bg']
        self.text_fill = cfg['text_fill']
        self.visions_source_path = cfg['visions_source_path']
        self.premium_paddings_k = cfg['premium_paddings_k']
        self.premium_size_k = cfg['premium_size_k']
        self.premium_img_path = cfg['premium_img_path']


    def draw(self, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO, card: str, vision: str = None, premium: int = None) -> BytesIO:
        text_filling = (self.text_fill[0], self.text_fill[1], self.text_fill[2], self.text_fill[3])
        # Загрузка шаблонных изображений.

        bg_path = self.backgrounds_path + card
        profile_bytes = Image.open(profile_bytes).convert(self.mode)
        im = Image.open(bg_path + "_Card.png").convert(self.mode)
        premium_img = Image.open(self.premium_img_path).convert(self.mode)
        im = im.resize((int(self.background_size[0]), int(self.background_size[1])))

        mask = Image.open(self.mask_path).convert(self.mode)
        exp_sign = Image.open(self.exp_img_path).convert(self.mode)


        # Размерим
        (width, height) = im.size
        resized_mask = mask.resize((width, height))
        resized_premium_img = premium_img.resize((int(premium_img.width * self.premium_size_k[0]), int(premium_img.height * self.premium_size_k[1])))
        premium_mask = resized_premium_img.copy()

        # Блюрим баннер
        #im = im.filter(ImageFilter.BLUR)

        # Сопоставление размера маски с размером баннера.
        #mask.resize(im.size)

        # Получаем размеры основного баннера


        # Создание портрета из изображения профиля.
        portret = make_portret(profile_bytes, self.portret_size)

        if premium:
            im.paste(resized_premium_img, (int(width * self.premium_paddings_k[0]), int(height * self.premium_paddings_k[1])), premium_mask)

        # Создание кисти
        im_draw = ImageDraw.Draw(im)

        # Наложение изображения профиля на баннер.
        im.paste(im=portret, box=(int(self.portret_paddings_k[0] * width), int(self.portret_paddings_k[1] * height)), mask=portret)

        # Наложение маски на баннер
        im.paste(resized_mask, resized_mask)

        # Наложение глаза бога
        if vision is not None:
            vision_path = self.visions_source_path + vision + self.format_file
            vision_img = Image.open(vision_path)
            resized_vision_img = vision_img.resize(
                (int(self.vision_size_k[0] * width), int(self.vision_size_k[1] * width)))
            im.paste(resized_vision_img,
                     (int(self.vision_padding_k[0] * width), int(self.vision_padding_k[1] * height)),
                     resized_vision_img)



        im.paste(exp_sign, (int(13/36 * width), int(38/60 * height)), exp_sign)

        xp_bar_rect = 10/24 * width, 170/240 * height,  17/18 * width, 174/240 * height
        xp_filled_bar_rect = 10/24 * width, 170/240 * height,  10/24 * width * (1 - xp / Profile.neededxp(rank)) + (xp / Profile.neededxp(rank) * 17/18 * width), 174/240 * height


        im_draw.text((int(41 / 108 * width), int(11 / 60 * height)), user, font=self.font, fill=text_filling)


        uid_text = f'UID {uid}'
        uid_pos = (int(18/288 * width), int(345/480 * height))
        im_draw.text(uid_pos, uid_text, font=self.medium_font, fill=text_filling)

        rank_text = f'{rank}'
        im_draw.text((int(96 / 108 * width), int(33 / 60 * height)), rank_text, font=self.font, fill=text_filling)

        rank_text_label = "Adventure Rank"
        im_draw.text((int(40 / 108 * width), int(34 / 60 * height)), rank_text_label, font=self.medium_font,
                     fill=text_filling)

        xp_text_label = "Adventure EXP"
        im_draw.text((int(15/36 * width), int(79/120 * height)), xp_text_label, font=self.small_font, fill=text_filling)

        needed_xp = self.neededxp(rank)
        xp_text = f'{xp}/{needed_xp}'
        xp_text_pos = (int(30/36 * width), int(79/120 * height))
        im_draw.text(xp_text_pos, xp_text, font=self.small_font, fill=text_filling)


        im_draw.rounded_rectangle(xy=xp_bar_rect, radius=100, fill=(0, 0, 0, 100))
        im_draw.rounded_rectangle(xy=xp_filled_bar_rect, radius=10, fill=(32, 223, 32, 220))


        count_chars_on_row = 25
        bio = string_cuts_on_rows(bio, count_chars_on_row)
        bio_text_position = (int(60 / 108 * width), int(22 / 60 * height))
        im_draw.text(bio_text_position, bio, font=self.small_font, fill=text_filling, anchor="ms")



        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        return buffer




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