import discord
from money_system.money_embed import Money_Embed
from money_system.money import update_money_db, get_money_db


async def give_money(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount <= 0:
        return await interaction.response.send_message("Аргумент `amount` должен быть строго положительный.", delete_after=5, ephemeral=True)
    giving_user = interaction.user
    reciever_user = user
    guild = interaction.guild
    await update_money_db(giving_user, guild, -amount)
    await update_money_db(reciever_user, guild, amount)
    return await interaction.response.send_message("Счёт обновлен", delete_after=5, ephemeral=True)


async def balance(interaction: discord.Interaction, user: discord.User = None) -> None:
    if user is not None:
        user = user
    else:
        user = interaction.user
    guild = interaction.guild
    current_money = await get_money_db(user, guild)
    embed = Money_Embed(user, current_money)
    return await interaction.response.send_message(embed=embed)
