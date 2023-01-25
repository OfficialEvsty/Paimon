from waifu_system.waifu import WaifuStats, Waifu
from data.database import Database
from discord import User, Guild, Member
import asyncpg

from waifu_system.waifu_logic import WaifuLogic


class Harem:
    def __init__(self, owner: User, guild: Guild):
        self.owner_id = owner.id
        self.guild: Guild = guild
        self.waifu_list = []

    def show(self) -> str:
        print(self.waifu_list)
        showing_string = ""
        for each in self.waifu_list:
            showing_string += f"Вайфу: {each.member.name}\nСтаты:\n" \
                              f"Уровень:{each.waifu_stats.lvl}\n" \
                              f"Удача:{each.waifu_stats.luck_attr}\n" \
                              f"Скорость:{each.waifu_stats.speed_attr}\n" \
                              f"Сила:{each.waifu_stats.strength_attr}\n" \
                              f"Прибыль:{each.waifu_stats.profit_attr}\n" \
                              f"Энергия:{each.waifu_stats.energy_attr}\n" \
                              f"Стоимость:{each.waifu_stats.cost}\n\n"
        return showing_string

    async def get_info(self):
        await self._get_waifus_from_db()

    async def _get_waifus_stats_from_db(self, waifus_records: asyncpg.Record, conn: asyncpg.Connection) -> []:
        guild: Guild = self.guild
        guild_id = self.guild.id

        waifu_list = []
        for i in range(len(waifus_records)):
            waifu_id = waifus_records[i][0]
            get_waifu_info_query = "SELECT energy, speed, profit, luck, strength, cost, lover, working_status, " \
                                   "resting_status " \
                                   "FROM waifu_stats " \
                                   f"WHERE guild = {guild_id} AND user_id = {waifu_id}"
            waifu_info_record = await conn.fetch(get_waifu_info_query)
            waifu_list_info = waifu_info_record[0]

            energy = waifu_list_info[0]
            speed = waifu_list_info[1]
            profit = waifu_list_info[2]
            luck = waifu_list_info[3]
            strength = waifu_list_info[4]
            cost = waifu_list_info[5]
            lover = waifu_list_info[6]
            is_working = waifu_list_info[7]
            is_resting = waifu_list_info[8]

            member = await guild.fetch_member(waifu_id)
            waifu_stats = WaifuStats(member=member, energy=energy, speed=speed, profit=profit, luck=luck,
                                     strength=strength, cost=cost, lover_user=lover, is_working=is_working,
                                     is_resting=is_resting)
            waifu = Waifu(member)
            waifu.waifu_stats = waifu_stats
            waifu.logic = WaifuLogic(waifu_stats)
            waifu_list.append(waifu)
        return waifu_list

    async def _get_waifus_from_db(self):
        guild_id = self.guild.id
        user_id = self.owner_id
        conn = await asyncpg.connect(Database.str_connection)
        get_waifus_list_query = "SELECT waifu " \
                                "FROM waifus " \
                                f"WHERE guild = {guild_id} AND owner = {user_id}"
        waifu_records = await conn.fetch(get_waifus_list_query)
        print(waifu_records)
        waifu_list = await self._get_waifus_stats_from_db(waifu_records, conn)

        await conn.close()
        self.waifu_list = waifu_list

    async def add_waifu(self, member: Member):
        conn = await asyncpg.connect(Database.str_connection)
        update_or_insert_waifu_sql = "DO $$ " \
                                     "BEGIN " \
                                        "IF EXISTS(" \
                                        "SELECT * FROM waifus " \
                                        f"WHERE guild = {member.guild.id} AND waifu = {member.id}) THEN " \
                                            f"UPDATE waifus SET owner = {self.owner_id}; " \
                                        f"ELSE " \
                                            f"INSERT INTO waifus (guild, owner, waifu) " \
                                            f"VALUES ({member.guild.id}, {self.owner_id}, {member.id}); " \
                                            f"INSERT INTO waifu_stats (guild, user_id) " \
                                            f"VALUES ({member.guild.id}, {member.id}); " \
                                     f"END IF;" \
                                     f"END $$;"
        await conn.fetch(update_or_insert_waifu_sql)
        waifu = Waifu(member)
        self.waifu_list.append(waifu)

    async def do_working(self, member: Member):
        waifu = self.find_waifu(member)
        await waifu.logic.work()

    def find_waifu(self, member: Member) -> Waifu:
        for waifu in self.waifu_list:
            if waifu.member.id == member.id:
                return waifu
            raise WaifuNotFound("Waifu not found in current list.")


class WaifuNotFound(Exception):
    def __init__(self, txt):
        self.txt = txt
