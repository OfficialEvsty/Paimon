import datetime

import discord
import transaction_system
from commands.cmd_guild_settings import get_transactions_channel
from utilities.embeds.transaction_embed import Transaction_Embed
from item_system.item import Item
from typing import Dict, List


class Transaction:
    def __init__(self, member: discord.Member, reason: str, money: int = None,
                 received_items: Dict[int, List[Item]] = None,
                 given_items: Dict[int, List[Item]] = None,
                 date: datetime.date = None):
        self.member: discord.Member = member
        self.reason: str = reason
        self.money: int = money
        self.received_items: {} = received_items
        self.given_items: {} = given_items
        self.date = f"Дата: {date}"

    async def send(self):
        transaction_channel = await get_transactions_channel(self.member.guild)
        if transaction_channel is None:
            return
        channel = transaction_channel
        transaction = Transaction_Embed(self.member, self.reason, self.money, self.received_items, self.given_items)
        await channel.send(embed=transaction)
        await transaction_system.transactions_bd.save(self)

    async def show(self, interaction: discord.Interaction):
        transaction = Transaction_Embed(self.member, self.reason, self.money, self.received_items, self.given_items,
                                        self.date)
        await interaction.followup.send(embed=transaction)
