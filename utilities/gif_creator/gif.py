from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO, StringIO


class Gif:
    def __init__(self, frames_IO: [], duration: int):
        self.frames_IO: [] = frames_IO
        self.duration: int = duration
        self.frames: [] = None

    def construct(self) -> BytesIO:
        if self.frames is None:
            raise FramesNotFound(self)

        buffer = BytesIO()
        self.frames[0].save(
            buffer,
            "gif",
            save_all=True,
            append_images=self.frames[1:],
            optimize=True,
            duration=self.duration,
            disposal=2,
            loop=0
        )
        return buffer


def get_img_file(gif_url: str):
    if gif_url[-4:] == ".gif":
        gif = urlopen(gif_url)
        return gif
    else:
        raise IncorrectGifURL(gif_url)



def convert_to_bytea(opened_gif_url) -> BytesIO:
    """with Image.open(opened_gif_url) as img:
        if not is_gif_size_valid(img.size):
            raise IncorrectGifSize(img.size)"""
    buffer = BytesIO(opened_gif_url.read())
    return buffer


def get_gif_frames(gif_bytes_io: BytesIO) -> Gif:
    frames = []
    with Image.open(gif_bytes_io) as gif:
        if not is_gif_size_valid(gif.size):
            raise IncorrectGifSize(gif.size)
        duration = gif.info['duration']
        for frame in ImageSequence.Iterator(gif):
            buffer = BytesIO()

            frame.save(buffer, 'png')
            frames.append(buffer)
    worked_gif = Gif(frames, duration, )
    return worked_gif


def is_gif_size_valid(size: ()) -> bool:
    template_size = (1092, 520)
    ratio_weight_to_height = template_size[0] // template_size[1]
    delta = 0.25
    current_ratio_weight_to_height = size[0] // size[1]

    if ratio_weight_to_height - delta <= current_ratio_weight_to_height <= ratio_weight_to_height + delta:
        return True
    else:
        return False


class IncorrectGifSize(Exception):
    def __init__(self, size: ()):
        self.text = f"Unsupported gif size: {size}"


class FramesNotFound(Exception):
    def __init__(self, gif_obj: Gif):
        self.obj = gif_obj
        self.text = f"Frames not found in {self.obj}"


class IncorrectGifURL(Exception):
    def __init__(self, url: str):
        self.text = f"Incorrect gif url: {url}"
