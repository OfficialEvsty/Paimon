from discord import User, Member
from utilities.randomizer import Randomizer
from waifu_system.waifu_storing.waifu_db import update_working_status, update_resting_status, upgrade_attribute, \
    update_cost_of_waifu
import json


# Class for storing waifus data.
# 0 - energy
# 1 - speed
# 2 - profit
# 3 - luck
# 4 - strength
class WaifuStats:
    def __init__(self, member: Member, energy: int = 0, speed: int = 0, profit: int = 0, luck: int = 0,
                 strength: int = 0, cost: int = 100, lover_user: User = None, is_working: bool = False,
                 is_resting: bool = False):
        self.member = member
        self.lvl = energy + speed + profit + luck + strength
        self.energy_attr = energy
        self.speed_attr = speed
        self.profit_attr = profit
        self.luck_attr = luck
        self.strength_attr = strength
        self.is_working = is_working
        self.is_resting = is_resting

        self.lover = lover_user

        self.cost = cost


# Waifu class represents profile of user, which became waifu on guild.
class Waifu:
    def __init__(self, member: Member):
        self.member = member
        self.guild = member.guild.id
        self.waifu_stats = None
        self.logic = None

    @staticmethod
    async def upgrade_waifu_attribute(member: Member):
        chances = []
        with open("waifu_system/config.json", 'r') as file:
            cfg = json.loads(file.read())
            for val in cfg.values():
                chances.append(val)

        randomizer = Randomizer(chances)
        index = randomizer.run()
        await upgrade_attribute(member, index)

    @staticmethod
    async def upgrade_waifu_cost(member: Member, level_cost: int):
        await update_cost_of_waifu(member, level_cost)

    @staticmethod
    async def update_working_status(member: Member, status: bool):
        await update_working_status(member, status)

    @staticmethod
    async def update_resting_status(member: Member, status: bool):
        await update_resting_status(member, status)

    async def work(self):
        await self.logic.work()








