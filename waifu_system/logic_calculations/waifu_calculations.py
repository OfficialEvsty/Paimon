from math import exp, log, sqrt
import json

with open("waifu_system/logic_calculations/logic_config.json", 'r') as file:
    cfg = json.loads(file.read())


def g_prog(beta: float, n: int, alpha: int = 1) -> int:
    result = alpha
    for index in range(n):
        result *= beta
    return result


def get_working_time(speed_lvl: int) -> int:
    base_time_working = cfg['base_working_time']
    const = cfg['speed_lvl_const']
    if speed_lvl < 2:
        modifier = exp((-speed_lvl) / (const + speed_lvl / (log(speed_lvl + 1) + 1)))
    else:
        modifier = exp((-speed_lvl) / (const + speed_lvl / log(speed_lvl)))
    working_time = base_time_working * modifier
    if working_time < 1:
        working_time = 1
    return int(working_time)


def get_resting_time(energy_lvl: int) -> int:
    base_time_resting = cfg['base_resting_time']
    const = cfg['speed_lvl_const']
    if energy_lvl < 2:
        modifier = exp((-energy_lvl) / (const + energy_lvl / (log(energy_lvl + 1) + 1)))
    else:
        modifier = exp((-energy_lvl) / (const + energy_lvl / log(energy_lvl)))
    resting_time = base_time_resting * modifier
    if resting_time < 1:
        resting_time = 1
    return int(resting_time)


def get_profit(profit_lvl: int, waifu_cost: int, strength_lvl: int):
    base_profit = cfg['base_money_profit']
    if strength_lvl > 2:
        cost_allowance = sqrt(2) * waifu_cost * log(strength_lvl) / 100
    else:
        cost_allowance = sqrt(2) * waifu_cost * (log(strength_lvl + 1) + 1) / 100
    modifier = log(profit_lvl + 1) + 1
    profit = (base_profit + cost_allowance) * modifier
    return int(profit)


def get_success_chance_of_working(strength_lvl: int) -> float:
    chance = 1 / (log(g_prog(beta=2.05, n=strength_lvl + 1, alpha=3)) / (log(g_prog(beta=2, n=strength_lvl + 1))))
    return chance


def get_drop_chance(luck_lvl: int, drop_chance: float, lvl: int) -> float:
    lvl_log_base = 10
    luck_modifier = log(luck_lvl+1) * log(lvl+1, lvl_log_base)
    drop_chance = luck_modifier * drop_chance
    if drop_chance > 1:
        drop_chance = 1
    return round(drop_chance, 4)


def get_drop_quantity(rand: float, luck_lvl: int, min_quantity: int = 1, max_quantity: int = 1) -> int:
    additional_quantity = round(log(luck_lvl+1) * min_quantity * rand)
    quantity = min_quantity + additional_quantity
    if quantity > max_quantity:
        quantity = max_quantity
    return quantity


def get_lvl_up_cost(lvl: int):
    base_lvl_up_cost = cfg['base_lvl_up_cost']
    lvl_cost = base_lvl_up_cost + base_lvl_up_cost * sqrt(lvl) * log(lvl + 1)
    return int(lvl_cost)

