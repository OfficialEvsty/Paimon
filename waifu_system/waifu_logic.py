from waifu_system.waifu import WaifuStats
from waifu_system.waifu_storing.waifu_db import update_working_status, update_resting_status
from waifu_system.logic_calculations.waifu_calculations import get_working_time, get_resting_time
import asyncio


class WaifuLogic:
    minute = 60
    hour = 60 * minute

    def __init__(self, stats: WaifuStats):
        self.stats: WaifuStats = stats
        self.is_working: bool = stats.is_working
        self.is_resting: bool = stats.is_resting

    async def on_work_end(self):
        print("закончил работу")
        # some function to give reward for owner.
        self.is_working = False
        await update_working_status(self.stats.member, self.is_working)
        await self.rest()
        pass

    async def work(self) -> bool:
        is_not_able_to_work = self.is_working or self.is_resting
        if is_not_able_to_work:
            return False
        working_time = get_working_time(self.stats.speed_attr)
        self.is_working = True
        await update_working_status(self.stats.member, self.is_working)
        print("начал работу")
        await asyncio.sleep(working_time)
        await self.on_work_end()

    async def rest(self):
        print("отдыхаю")
        self.is_resting = True
        await update_resting_status(self.stats.member, self.is_resting)
        resting_time = get_resting_time(self.stats.energy_attr)
        await asyncio.sleep(resting_time)
        self.is_resting = False
        await update_resting_status(self.stats.member, self.is_resting)
        pass


