from transaction_system.transactions_bd import get_transactions, get_transaction
from utilities.embeds.transaction_list import TransactionList
from discord import Member, Interaction


async def get_member_transactions(interaction: Interaction, member: Member, days: int = 7):
    await interaction.response.defer()
    dict_transactions = await get_transactions(member, days)
    actions_list = TransactionList(member, dict_transactions)
    await interaction.followup.send(embed=actions_list)


async def get_transaction_by_id(interaction: Interaction, transaction_id: int):
    await interaction.response.defer()
    transaction = await get_transaction(interaction, transaction_id)
    await transaction.show(interaction)
