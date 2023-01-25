import time
from urllib.request import urlopen, Request
from http.client import HTTPResponse
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO, StringIO


class Gif:
    def __init__(self, frames_IO: [], duration: int):
        self.frames_IO: [] = frames_IO
        self.duration: int = duration
        self.frames: [] = None

    def __await__(self):
        async def closure():
            # We can await in here
            return self

        return closure().__await__()

    def construct(self) -> BytesIO:
        if self.frames is None:
            raise FramesNotFound(self)
        print(self.frames)
        start = time.monotonic()
        buffer = BytesIO()
        self.frames[0].save(
            buffer,
            "gif",
            save_all=True,
            append_images=self.frames[1:],
            optimize=True,
            duration=self.duration,
            disposal=2,
            loop=0,
            compress_level=1,
            compress_type=3
        )
        end = time.monotonic()
        print(f"Время сбора гифки: {end - start}")
        return buffer


def get_img_file(gif_url: str):
    if gif_url[-4:] == ".gif":
        req = Request(
            url=gif_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        gif = urlopen(req)
        return gif
    else:
        raise IncorrectGifURL(gif_url)


def convert_to_bytea(opened_gif_url: HTTPResponse) -> BytesIO:
    buffer = BytesIO(opened_gif_url.read())
    with Image.open(buffer) as gif:
        if not is_gif_size_valid(gif.size):
            raise IncorrectGifSize(gif.size)
        if gif.n_frames > 250:
            raise MuchFramesInGif(gif.n_frames)

    return buffer


async def get_gif_frames(gif_bytes_io: BytesIO) -> Gif:
    frames = []
    with Image.open(gif_bytes_io) as gif:
        duration = gif.info['duration']
        start_ = time.monotonic()
        for frame in ImageSequence.Iterator(gif):
            start = time.monotonic()
            buffer = BytesIO()
            frame.save(buffer, 'png', compress_level=1, compress_type=3)
            end = time.monotonic()
            print(end - start)
            frames.append(buffer)
    worked_gif = Gif(frames, duration)
    end_ = time.monotonic()
    print(end_ - start_)
    return worked_gif




def is_gif_size_valid(size: ()) -> bool:
    template_size = (1092, 520)
    ratio_weight_to_height = template_size[0] / template_size[1]
    delta = 0.4
    current_ratio_weight_to_height = size[0] / size[1]
    print(current_ratio_weight_to_height, ratio_weight_to_height, delta)

    if ratio_weight_to_height - delta <= current_ratio_weight_to_height <= ratio_weight_to_height + delta:
        return True
    else:
        return False


class MuchFramesInGif(Exception):
    def __init__(self, count_frames):
        self.text = f"Gif has too much frames {count_frames}."


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
