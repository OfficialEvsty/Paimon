import discord
from waifu_system.waifu import Waifu
from data.database import Database
from discord import Member
from waifu_system.waifu_storing.waifu_db import get_waifus_from_db, get_waifu_stats_from_db, add_waifu, \
    if_exists_get_else_insert_waifu_owner, remove_owner
from waifu_system.exceptions import WaifuNotFound
from typing import List
import asyncpg

from waifu_system.waifu_logic import WaifuLogic


class Harem:
    def __init__(self, owner: Member):
        self.owner = owner
        self.waifu_owner: Waifu = None
        self.waifus: List[Waifu] = []

    def show(self) -> str:
        print(self.waifus)
        showing_string = ""
        for each in self.waifus:
            showing_string += f"Вайфу: {each.member.name}\nСтаты:\n" \
                              f"Уровень:{each.stats.lvl}\n" \
                              f"Удача:{each.stats.luck_attr}\n" \
                              f"Скорость:{each.stats.speed_attr}\n" \
                              f"Сила:{each.stats.strength_attr}\n" \
                              f"Прибыль:{each.stats.profit_attr}\n" \
                              f"Энергия:{each.stats.energy_attr}\n" \
                              f"Стоимость:{each.stats.cost}\n\n"
        return showing_string

    async def __get_owner(self, conn: asyncpg.Connection) -> Waifu:
        waifu_id, owner_id = await if_exists_get_else_insert_waifu_owner(self.owner, conn)
        waifu = await self.owner.guild.fetch_member(waifu_id)

        if owner_id:
            try:
                owner = await self.owner.guild.fetch_member(owner_id)
            except discord.NotFound:
                await remove_owner(waifu, conn)
                owner = None
        else:
            owner = None

        stats = await get_waifu_stats_from_db(waifu.guild, waifu_id, conn)
        logic = WaifuLogic(stats)
        waifu = Waifu(stats, logic, owner)
        return waifu

    async def get_waifus(self):
        conn = await asyncpg.connect(Database.str_connection)
        self.waifu_owner = await self.__get_owner(conn)
        waifu_records = await get_waifus_from_db(self.owner, conn)
        for waifu_list in waifu_records:
            waifu_id = waifu_list[0]
            try:
                stats = await get_waifu_stats_from_db(self.owner.guild, waifu_id, conn)
            except WaifuNotFound:
                continue
            logic = WaifuLogic(stats)
            waifu = Waifu(stats, logic, self.owner)
            self.waifus.append(waifu)
        await conn.close()

    async def add_waifu(self, owner: Member, member: Member):
        stats = await add_waifu(owner, member)
        logic = WaifuLogic(stats)
        waifu = Waifu(stats, logic, self.owner)
        self.waifus.append(waifu)

    async def do_working(self, member: Member):
        waifu = self.find_waifu(member)
        await waifu.logic.work(self.owner)

    def find_waifu(self, member: Member) -> Waifu:
        for waifu in self.waifus:
            if waifu.member.id == member.id:
                return waifu



