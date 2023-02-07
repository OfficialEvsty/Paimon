import discord
from discord import Interaction, Member
from waifu_system.harem import Harem
from waifu_system.harem_interaction import HaremInteraction
from waifu_system.waifu_storing.waifu_db import change_waifu_attrs
from waifu_system.waifu import Waifu
from bot_ui_kit.ui_waifu import UI_WaifuView
from utilities.embeds.waifu_embed import WaifuEmbed


async def show_my_waifu_profile(interaction: Interaction):
    # gui
    # ui
    # database pulling
    pass


async def show_waifu(waifu: Waifu):
    pass


async def show_profile(interaction: Interaction, inter: HaremInteraction = None, ui: UI_WaifuView = None,
                       chosen_index: int = 0, info_mode: bool = False,
                       member: Member = None):
    if member:
        if interaction.user.id == member.id:
            member_id = member.id
            is_mine = True
        else:
            member_id = member.id
            is_mine = False
    else:
        member_id = interaction.user.id
        is_mine = True

    try:
        member_ = await interaction.guild.fetch_member(member_id)
    except discord.NotFound:
        return await interaction.response.send_message("Данного пользователя нету на сервере.", ephemeral=True,
                                                       delete_after=5)

    await interaction.response.defer(ephemeral=True)
    if not inter:
        default_harem = Harem(member_)
        await default_harem.get_waifus()
        inter = HaremInteraction(default_harem, chosen_index)
    if not ui:
        ui = UI_WaifuView(inter, is_mine=is_mine)

    if interaction.message:
        webhook_id = interaction.message.id

        if inter:
            if not ui:
                ui = UI_WaifuView(inter, is_mine=is_mine)
        if info_mode:
            embed = WaifuEmbed(inter.chosen.stats)
            original = await interaction.followup.edit_message(message_id=webhook_id, view=ui, embed=embed)
            ui.original = original
            return
        original = await interaction.followup.edit_message(message_id=webhook_id, view=ui, embed=None)
        ui.original = original
        return
    else:
        original = await interaction.followup.send("фафа", view=ui)
        ui.original = original
        return






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
