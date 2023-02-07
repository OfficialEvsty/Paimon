from discord import Member
from waifu_system.waifu_logic import WaifuLogic, WaifuStats
from utilities.randomizer import Randomizer
from waifu_system.waifu_storing.waifu_db import update_working_status, update_resting_status, upgrade_attributes, \
    update_cost_of_waifu
import json


# Waifu class represents profile of user, which became waifu on guild.
class Waifu:
    def __init__(self, stats: WaifuStats, logic: WaifuLogic, owner: Member = None):
        self.member = stats.member
        self.owner = owner
        self.stats = stats
        self.logic = logic

    async def upgrade_waifu_attributes(self, levels: int = 1):
        chances = []
        with open("waifu_system/config.json", 'r') as file:
            cfg = json.loads(file.read())
            for val in cfg.values():
                chances.append(val)

        randomizer = Randomizer(chances)
        await upgrade_attributes(self.member, randomizer, levels)

    @staticmethod
    async def upgrade_waifu_cost(interacting: Member, member: Member, level_cost: int):
        await update_cost_of_waifu(member, level_cost)

    @staticmethod
    async def update_working_status(interacting: Member, member: Member, status: bool):
        await update_working_status(interacting, member, status)

    @staticmethod
    async def update_resting_status(interacting: Member, member: Member, status: bool):
        await update_resting_status(interacting, member, status)

    async def work(self):
        await self.logic.work(self.owner)

    async def gift(self):
        is_gift_ready = await self.logic.take_gift(self.owner, self.stats)
        await self.logic.work(self.owner)








