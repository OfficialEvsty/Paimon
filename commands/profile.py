from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class Profile:
    def __init__(self) -> None:
        path = "utilities/fonts/zh-cn.ttf"
        self.font = ImageFont.truetype(path, 46)
        self.medium_font = ImageFont.truetype(path, 40)
        self.small_font = ImageFont.truetype(path, 22)

    def draw(self, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO) -> BytesIO:
        profile_bytes = Image.open(profile_bytes)
        im = Image.open("utilities/card_backgrounds/Eula_Card.jpg")
        exp_sign = Image.open("utilities/card_fillers/EXP.png").convert('RGBA')
        (width, height) = im.size
        im.paste(exp_sign, (int(13/36 * width), int(38/60 * height)), exp_sign)
        xp_bar_rect = 10/24 * width, 43/60 * height,  17/18 * width, 44/60 * height
        xp_filled_bar_rect = 10/24 * width, 43/60 * height,  10/24 * width + (xp / Profile.neededxp(rank) * 17/18 * width), 44/60 * height

        im_draw = ImageDraw.Draw(im)
        im_draw.text((int(40 / 108 * width), int(10 / 60 * height)), user, font=self.font, fill=(255, 255, 255, 255))

        im_draw.rounded_rectangle((3/12 * width, 23/24 * height, 9/12 * width, 25/24 * height), fill=(0, 0, 0, 0),
                               width=5, radius=100)


        print(bio)
        bio_text_position = (int(40 / 108 * width), int(18 / 60 * height))
        im_draw.text(bio_text_position, bio, font=self.small_font, fill=(255, 255, 255, 255))

        uid_text = f'UID {uid}'
        uid_pos = (int(1/36 * width), int(38/60 * height))
        im_draw.text(uid_pos, uid_text, font=self.medium_font, fill=(255, 255, 255, 255))

        rank_text = f'{rank}'
        im_draw.text((int(96 / 108 * width), int(33 / 60 * height)), rank_text, font=self.font, fill=(255, 255, 255, 255))

        rank_text_label = "Adventure Rank"
        im_draw.text((int(40 / 108 * width), int(34 / 60 * height)), rank_text_label, font=self.medium_font,
                     fill=(255, 255, 255, 255))

        xp_text_label = "Adventure EXP"
        im_draw.text((int(15/36 * width), int(79/120 * height)), xp_text_label, font=self.small_font, fill=(255, 255, 255, 255))

        needed_xp = self.neededxp(rank)
        xp_text = f'{xp}/{needed_xp}'
        xp_text_pos = (int(30/36 * width), int(79/120 * height))
        im_draw.text(xp_text_pos, xp_text, font=self.small_font, fill=(255, 255, 255, 255))


        im_draw.rectangle(xp_bar_rect, fill=(0, 0, 0, 100))
        im_draw.rectangle(xp_filled_bar_rect, fill=(32, 223, 32, 200))

        #Making profile portret
        size = (256, 256)
        portret = crop(profile_bytes, size)
        portret.putalpha(prepare_mask(size, 4))


        im.paste(portret, (50, 50), portret)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)

        return buffer



    @staticmethod
    def neededxp(level: int) -> int:
        print(level)
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