from discord import Interaction, Member
from waifu_system.harem import Harem
from waifu_system.waifu_storing.waifu_db import change_waifu_attrs


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


async def set_attrs_waifu(member: Member, speed: int = None, energy: int = None,
                          profit: int = None, strength: int = None, luck: int = None):
    await change_waifu_attrs(member, speed=speed, energy=energy, profit=profit, strength=strength, luck=luck)
