import time

from card_profile.profile import Profile
from PIL import Image, ImageFont
from utilities.gif_creator.gif import Gif, get_gif_frames
from io import BytesIO


class Premium_Profile(Profile):
    def __init__(self, gif: Gif, size: () = None):
        super().__init__(size)
        self.gif = gif
        self.font = ImageFont.truetype(self.path, 24)
        self.medium_font = ImageFont.truetype(self.path, 18)
        self.small_font = ImageFont.truetype(self.path, 12)

    async def draw(self, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO, card: str = None,
             vision: str = None, premium: int = None, is_hoyolab: bool = False) -> Gif:
        gif_frames = []
        frames_IO = self.gif.frames_IO
        start = time.monotonic()
        for frame_io in frames_IO:
            im = Image.open(frame_io).convert("RGBA")
            draw_frame = await self.draw_content(im=im, user=user, uid=uid, bio=bio, rank=rank, xp=xp, profile_bytes=profile_bytes,
                              vision=vision, premium=premium, is_hoyolab=is_hoyolab)

            gif_frames.append(draw_frame)
        self.gif.frames = gif_frames
        end = time.monotonic()
        print(end - start)
        return await self.gif

