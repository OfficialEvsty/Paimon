import discord
from commands.cmd_guild_settings import get_transactions_channel
from utilities.embeds.transaction_embed import Transaction_Embed


class Transaction:
    def __init__(self, member: discord.Member, reason: str, money: int = None, received_items: [] = None,
                 given_items: [] = None):
        self.member: discord.Member = member
        self.reason: str = reason
        self.money: int = money
        self.received_items: [] = received_items
        self.given_items: [] = given_items

    async def send(self):
        transaction_channel = await get_transactions_channel(self.member.guild)
        if transaction_channel is None:
            return
        channel = transaction_channel
        transaction = Transaction_Embed(self.member, self.reason, self.money, self.received_items, self.given_items)
        await channel.send(embed=transaction)