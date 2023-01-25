from discord import Interaction, Member
from waifu_system.harem import Harem


async def show_harem(interaction: Interaction):
    user = interaction.user
    guild = interaction.guild
    harem = Harem(user, guild)
    await harem.get_info()
    return harem.show()


async def claim_waifu(interaction: Interaction, member: Member):
    user = interaction.user
    guild = interaction.guild
    harem = Harem(user, guild)
    await harem.add_waifu(member)
