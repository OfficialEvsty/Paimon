from waifu_system.waifu_storing.waifu_db import update_working_status, update_resting_status, update_gift_status
from waifu_system.logic_calculations.waifu_calculations import get_working_time, get_resting_time
from waifu_system.waifu_gift import WaifuGift, WaifuStats
from transaction_system.transaction import Transaction
from discord import Member
import asyncio


class WaifuLogic:
    minute = 60
    hour = 60 * minute

    def __init__(self, stats: WaifuStats):
        self.stats: WaifuStats = stats
        self.is_working: bool = stats.is_working
        self.is_resting: bool = stats.is_resting
        self.is_gift_ready: bool = stats.is_gift_ready

    async def take_gift(self, owner: Member, stats: WaifuStats) -> bool:
        if not self.is_gift_ready:
            return False
        self.is_gift_ready = False
        await update_gift_status(owner, self.stats.member, self.is_gift_ready)
        # Creating a waifu gift.
        gift = WaifuGift(owner, stats)
        await gift.apply()

        reason = f"Получил подарок от вайфу {stats.member}"
        transaction = Transaction(owner, reason, gift.money, received_items=gift.items)
        await transaction.send()
        await self.on_gift_taken(owner)
        return True

    async def on_gift_taken(self, owner: Member):
        await self.work(owner)

    async def on_work_end(self, interacting: Member):
        print("закончил работу")
        self.is_working = False
        await update_working_status(interacting, self.stats.member, self.is_working)
        self.is_gift_ready = True
        await update_gift_status(interacting, self.stats.member, self.is_gift_ready)
        await self.rest(interacting)

    async def work(self, interacting: Member) -> bool:
        is_not_able_to_work = self.is_working or self.is_resting or self.is_gift_ready
        if is_not_able_to_work:
            return False
        working_time = get_working_time(self.stats.speed_attr)
        self.is_working = True
        await update_working_status(interacting, self.stats.member, self.is_working)
        print("начал работу")
        await asyncio.sleep(working_time)
        await self.on_work_end(interacting)

    async def rest(self, interacting: Member):
        print("отдыхаю")
        self.is_resting = True
        await update_resting_status(interacting, self.stats.member, self.is_resting)
        resting_time = get_resting_time(self.stats.energy_attr)
        await asyncio.sleep(resting_time)
        self.is_resting = False
        await update_resting_status(interacting, self.stats.member, self.is_resting)
        await self.work(interacting)



