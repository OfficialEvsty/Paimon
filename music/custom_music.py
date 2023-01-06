import wavelink
import discord
from bot_ui_kit.ui_music_interaction import UI_MusicView
from discord.ext import commands


class CustomPlayer(wavelink.Player):

    def __init__(self, msg: discord.Message = None):
        super().__init__()
        self.queue = wavelink.Queue()
        self.src_msg: discord.Message = msg




# commands


async def connect(ctx):
    vc = ctx.voice_client # represents a discord voice connection
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return await ctx.send("Please join a voice channel to connect.")

    if not vc:
        await ctx.author.voice.channel.connect(cls=CustomPlayer())
    else:
        await ctx.send("The bot is already connected to a voice channel")



async def play(interaction: discord.Interaction, search: str):
    vc = interaction.client.voice_clients
    print(vc)
    track = await wavelink.YouTubeTrack.search(query=search, return_first=True)
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await interaction.user.voice.channel.connect(cls=custom_player)
    if vc:
        vc = interaction.guild.voice_client
    if vc.is_playing():
        await interaction.response.defer(thinking=False)
        vc.queue.put(item=track)

        await interaction.followup.send(f"Queued {track.title} in {vc.channel}")
    else:
        await vc.play(track)

        view = UI_MusicView(vc.queue)
        view = view.create_view()

        msg = await interaction.response.send_message(embed=discord.Embed(
            title=vc.source.title,
            url=vc.source.uri,
            description=f"Играет {vc.source.title} в {vc.channel}"
        ), view=view)
        vc.src_msg = msg


async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        if not vc.is_playing():
            return await interaction.followup.send("Nothing is playing.", delete_after=5)
        if vc.queue.is_empty:
            return await vc.stop()

        await vc.seek(vc.track.length * 1000)
        embed = discord.Embed(
            title=vc.source.title,
            url=vc.source.uri,
            description=f"Играет {vc.source.title} в {vc.channel}"
        )
        await interaction.message.edit()
        if vc.is_paused():
            await vc.resume()
    else:
        await interaction.followup.send("The bot is not connected to a voice channel.", delete_after=5)


async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.pause()
        else:
            await interaction.followup.send("Nothing is playing.", delete_after=5)
    else:
        await interaction.followup.send("The bot is not connected to a voice channel", delete_after=5)


async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        if vc.is_paused():
            await vc.resume()
        else:
            await interaction.followup.send("Nothing is paused.", delete_after=5)
    else:
        await interaction.followup.send("The bot is not connected to a voice channel", delete_after=5)


# error handling

async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Could not find a track.")
    else:
        await ctx.send("Please join a voice channel.")
