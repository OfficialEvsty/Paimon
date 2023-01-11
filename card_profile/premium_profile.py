import time

from card_profile.profile import Profile
from PIL import Image
from utilities.gif_creator.gif import Gif, get_gif_frames
from io import BytesIO


class Premium_Profile(Profile):
    def __init__(self, gif: Gif):
        super().__init__()
        self.gif = gif

    async def draw(self, user: str, uid: str, bio: str, rank: int, xp: int, profile_bytes: BytesIO, card: str = None,
             vision: str = None, premium: int = None) -> Gif:
        gif_frames = []
        frames_io = self.gif.frames_IO
        start = time.monotonic()
        for frame_io in frames_io:

            im = Image.open(frame_io).convert("RGBA")
            frame = await self.draw_content(im=im, user=user, uid=uid, bio=bio, rank=rank, xp=xp, profile_bytes=profile_bytes,
                              vision=vision, premium=premium)
            gif_frames.append(frame)
        self.gif.frames = gif_frames
        end = time.monotonic()
        print(end - start)
        return await self.gif

