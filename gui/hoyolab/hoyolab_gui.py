import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.request import urlopen


class Hoyolab_GUI:
    def __init__(self, ):
        with open("gui/hoyolab/hoyolab_settings.json") as file:
            self.cfg = json.loads(file.read())
        self.font_path = self.cfg["font_path"]
        self.font_big_size = self.cfg["font_big_size"]
        self.font = ImageFont.truetype(self.font_path, self.font_big_size)
        self.small_font = ImageFont.truetype(self.font_path, self.cfg["font_small_size"])
        text_fill = self.cfg["text_fill"]
        self.fill = (text_fill[0], text_fill[1], text_fill[2], text_fill[3])

        bg_size_list = self.cfg["bg_size"]
        self.bg_size = (bg_size_list[0], bg_size_list[1])
        icon_size_list = self.cfg["icon_size"]
        self.icon_size = (icon_size_list[0], icon_size_list[1])
        icon_paddings_k_list = self.cfg["icon_paddings_k"]
        self.icon_paddings = (int(icon_paddings_k_list[0] * bg_size_list[0]),
                              int(icon_paddings_k_list[1] * bg_size_list[1]))
        crop_k = self.cfg["crop_k"]
        self.crop_coords = (0, 0, bg_size_list[0], int(bg_size_list[1] * crop_k))
        panel_color_theme = self.cfg["panel_color"]
        self.panel_color = (panel_color_theme[0], panel_color_theme[1], panel_color_theme[2],
                            panel_color_theme[3])
        self.panel_size = (bg_size_list[0], bg_size_list[1] - self.crop_coords[3])
        self.icon_border_delta = 6
        self.icon_border_paddings = (self.icon_paddings[0] - self.icon_border_delta // 2,
                                     self.icon_paddings[1] - self.icon_border_delta // 2)
        self.icon_border_size = (icon_size_list[0] + self.icon_border_delta, icon_size_list[1] + self.icon_border_delta)
        self.icon_border_color = (panel_color_theme[0] + 40, panel_color_theme[1] + 40, panel_color_theme[2] + 40,
                                  panel_color_theme[3])

        nickname_paddings_k = self.cfg["nickname_paddings_k"]
        self.nickname_paddings = (nickname_paddings_k[0] * self.panel_size[0],
                                  nickname_paddings_k[1] * self.panel_size[1])

        level_box_size_k = self.cfg["level_box_size_k"]
        self.level_box_size = (int(level_box_size_k[0] * self.panel_size[0]), int(level_box_size_k[1] * self.panel_size[0]))
        self.level_box_color = (self.cfg["level_box_color"][0], self.cfg["level_box_color"][1], self.cfg["level_box_color"][2],
                                self.cfg["level_box_color"][3])
        #self.nickname_align = self.cfg["nickname_align"]

    def draw(self, bg_url: str, icon_url: str, name: str, lvl: int = None, uid: int = None) -> BytesIO:
        bg_img_url = urlopen(bg_url)
        icon_img_url = urlopen(icon_url)
        bg_img = Image.open(fp=bg_img_url).convert(mode="RGBA")
        croped_bg_img = bg_img.crop(self.crop_coords)
        icon_img = Image.open(fp=icon_img_url).convert(mode="RGBA")
        icon_portret = make_portret(icon_img, self.icon_size)
        icon_border = Image.new(mode="RGBA", size=self.icon_border_size, color=self.icon_border_color)
        portret_border = make_portret(icon_border, self.icon_border_size)
        panel_bottom = Image.new(mode="RGBA", size=self.panel_size, color=self.panel_color)
        level_box = Image.new(mode="RGBA", size=self.level_box_size, color=self.level_box_color)
        rounded_level_box = make_portret(level_box, self.level_box_size)

        im_draw = ImageDraw.Draw(panel_bottom)

        im_draw.text(self.nickname_paddings, text=name, fill=self.fill, font=self.font)

        num_characters_in_name = len(name)
        pixel_on_character = 28
        deviation = int(num_characters_in_name * pixel_on_character)
        box_draw = ImageDraw.Draw(rounded_level_box)

        box_draw.text((int(self.level_box_size[0] * 0.15), int(self.level_box_size[1] * 0.3)), text=f"lvl.{lvl}", font=self.small_font,
                      align="center")

        right_padding = 25
        im_draw.text(xy=(self.panel_size[0] - right_padding, self.nickname_paddings[1]), text=f"ID: {uid}", fill=self.fill,
                      font=self.font, anchor="ra")

        panel_bottom.paste(rounded_level_box, (int(self.nickname_paddings[0] + deviation), int(self.nickname_paddings[1])), rounded_level_box)
        croped_bg_img.paste(panel_bottom, (0, croped_bg_img.height - panel_bottom.height))
        croped_bg_img.paste(portret_border, self.icon_border_paddings, portret_border)
        croped_bg_img.paste(icon_portret, self.icon_paddings, icon_portret)


        buffer = BytesIO()
        croped_bg_img.save(fp=buffer, format='png')
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