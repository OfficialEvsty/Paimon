from discord import Embed
from waifu_system.waifu_stats import WaifuStats
from waifu_system.logic_calculations.waifu_calculations import *


class WaifuEmbed(Embed):
    def __init__(self, stats: WaifuStats):
        super().__init__()
        success_gift_per = get_success_chance_of_working(stats.strength_attr) * 100
        speed_hours = get_working_time(stats.speed_attr)
        energy_hours = get_resting_time(stats.energy_attr)
        profit_per = get_profit(stats.profit_attr, stats.cost, stats.strength_attr)
        status = ""
        if stats.is_resting:
            status = "Отдыхает Zzz..."
        elif stats.is_working:
            status = "Собирает подарок..."
        elif stats.is_gift_ready:
            status = "Хочет отдать подарок."
        self.title = f"**Статус:** `{status}`"
        self.description = f">>> **Шанс успешного подарка:**\n" \
                           f"`{success_gift_per}`%\n" \
                           f"**Время сбора подарков:\n**" \
                           f"`{speed_hours}`ч\n" \
                           f"**Время отдыха:**\n" \
                           f"`{energy_hours}`ч\n" \
                           f"**Прибыль:**\n" \
                           f"`{profit_per}`%\n"

