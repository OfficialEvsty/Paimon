import discord
import discord.app_commands
from card_profile.profile import Profile
from discord import File as dFile
from bot import Bot
from io import BytesIO
import aiohttp

async def cmd_card(interaction: discord.Interaction, user: discord.Member = None) -> None:

    if user is None:
        user = interaction.user

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{user.avatar}?size=512') as resp:
            profile_bytes = await resp.read()
    table = "users"
    guild_id = interaction.guild.id
    user_id = interaction.user.id
    cols_list = ["xp", "rank", "uid", "bio"]
    condition_pattern = "AND"
    dict_conditions = {"id" : user_id, "guild" : guild_id}
    result = await Bot.db.get_db(table, await Bot.db.filter(condition_pattern, dict_conditions), cols_list)
    validation = False
    if result:
        validation = result[0][0] is not None and result[0][1] is not None and result[0][2] is not None and result[0][3] is not None
    if validation is not True:
        return await interaction.response.send_message(f'{user} ещё не зарегистрирован в Гильдии искателей приключений.')

    xp = result[0][0]
    rank = result[0][1]
    uid = result[0][2]
    bio = result[0][3]
    card = "Albedo"

    profilecard = Profile()
    buffer = profilecard.draw(str(user), uid, bio, rank, xp, BytesIO(profile_bytes), card)


    return await interaction.response.send_message(file=dFile(fp=buffer, filename='rank_card.png'))






