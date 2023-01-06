import discord
from money_system.money_embed import Money_Embed
from money_system.money import update_money_db, get_money_db
from transaction_system.transaction import Transaction
from global_modifiers.modifier import Modifier


async def give_money(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount <= 0:
        return await interaction.response.send_message("Аргумент `amount` должен быть строго положительный.", delete_after=5, ephemeral=True)
    giving_user = interaction.user
    reciever_user = user
    guild = interaction.guild
    await update_money_db(giving_user, guild, -amount)
    await update_money_db(reciever_user, guild, amount)

    money = amount
    give_reason = f"Подарил пользователю {reciever_user}"
    transaction = Transaction(giving_user, give_reason, -money)
    await transaction.send()
    take_reason = f"Получил от пользователя {giving_user}"
    transaction = Transaction(reciever_user, take_reason, money)
    await transaction.send()

    return await interaction.response.send_message("Счёт обновлен", delete_after=5, ephemeral=True)


async def balance(interaction: discord.Interaction, user: discord.User = None) -> None:
    if user is not None:
        user = user
    else:
        user = interaction.user
    guild = interaction.guild
    current_money = await get_money_db(user, guild)
    money_modifier = Modifier(user, guild)
    await money_modifier.init()
    money_modifiers_str = ""
    for (key, value) in money_modifier.money_modifiers_dict.items():
        money_modifiers_str += f"⎢ `{key}`: `+` `x{round(value, 1)}`\n"
    embed = Money_Embed(user, current_money)
    if money_modifiers_str == "":
        money_modifiers_str = "У вас пока что нету усилителей."
    embed.add_field(name=f"⎢ Общий бонус от усилителей: "
                         f"`x{round(money_modifier.money_modifier - money_modifier.default_money_earn, 1)}`",
                    value=money_modifiers_str)
    return await interaction.response.send_message(embed=embed)
