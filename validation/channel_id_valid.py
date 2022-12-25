import discord


def is_channel_id_valid(guild: discord.Guild, channel: discord.TextChannel) -> bool:
    for chan in guild.channels:
        if chan.id == channel.id:
            return True
    return False
