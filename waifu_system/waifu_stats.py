from discord import Member, User

# Class for storing waifus data.
# 0 - energy
# 1 - speed
# 2 - profit
# 3 - luck
# 4 - strength


class WaifuStats:
    def __init__(self, member: Member, energy: int = 0, speed: int = 0, profit: int = 0, luck: int = 0,
                 strength: int = 0, cost: int = 100, lover_user: User = None, is_working: bool = False,
                 is_resting: bool = False, is_gift_ready: bool = False):
        self.member = member
        self.lvl = energy + speed + profit + luck + strength
        self.energy_attr = energy
        self.speed_attr = speed
        self.profit_attr = profit
        self.luck_attr = luck
        self.strength_attr = strength
        self.is_working = is_working
        self.is_resting = is_resting
        self.is_gift_ready = is_gift_ready

        self.lover = lover_user

        self.cost = cost