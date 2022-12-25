import aiohttp
import discord
from io import BytesIO
from gui.levelup_gui import LevelUp_GUI
from commands.cmd_guild_settings import get_notifications_channel


async def level_up_gui(guild: discord.Guild, user: discord.User, rank: int) -> None:

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{user.avatar}?size=512') as resp:
            profile_bytes = await resp.read()

    gui = LevelUp_GUI()
    buffer = gui.draw(str(user), rank, BytesIO(profile_bytes))
    dFile = discord.File(fp=buffer, filename="level_up_img.png")
    channel_id = await get_notifications_channel(guild)
    if channel_id is None:
        return
    channel = guild.get_channel(channel_id)
    await channel.send(file=dFile)




