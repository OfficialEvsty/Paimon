from rewarding.reward import Reward
from waifu_system.waifu_stats import WaifuStats
from waifu_system.logic_calculations.waifu_calculations import get_drop_chance, get_drop_quantity, get_profit
from item_system.generator import Generator
from utilities.randomizer import Randomizer
from discord import Member
import json


class WaifuGift(Reward):
    def __init__(self, owner: Member, stats: WaifuStats):
        self.lvl = stats.lvl
        self.luck_lvl = stats.luck_attr
        self.profit_lvl = stats.profit_attr
        self.strength_lvl = stats.strength_attr
        self.waifu_cost = stats.cost
        self.owner = owner

        money = self._add_money()
        items = self._add_items()

        super().__init__(guild=self.owner.guild, user=self.owner, money=money, items=items)

    def _add_money(self) -> int:
        return get_profit(self.profit_lvl, self.waifu_cost, self.strength_lvl)

    def _add_items(self) -> {}:
        with open("waifu_system/gifts.json", 'r') as file:
            gifts: dict = json.loads(file.read())
        item_chances_to_drop = []
        for item_id, info in gifts.items():
            item_chances_to_drop.append(info['chance'])

        modified_item_chances_to_drop = []
        for index in range(len(item_chances_to_drop)):
            modified_item_chances_to_drop.append(get_drop_chance(self.luck_lvl, item_chances_to_drop[index], self.lvl))

        randomizer = Randomizer(modified_item_chances_to_drop)

        selected_item_types = WaifuGift._create_list_chosen_item_types(randomizer, gifts)

        return self._create_items(selected_item_types, gifts)

    @staticmethod
    def _create_list_chosen_item_types(randomizer: Randomizer, gifts_dict: {}) -> []:
        selected_indexes = randomizer.run_each()
        selected_item_types = []
        counter = 0
        for index in selected_indexes:
            for item_type in gifts_dict.keys():
                if index == counter:
                    selected_item_types.append(int(item_type))
                counter += 1
        return selected_item_types

    def _create_items(self, selected_item_types: [], gifts_dict: {}) -> {}:
        items = {}
        count = 0
        for item_type in selected_item_types:
            key_type = str(item_type)
            if key_type in gifts_dict.keys():
                min_q = gifts_dict[key_type]['min_count']
                max_q = gifts_dict[key_type]['max_count']
                quantity = get_drop_quantity(Randomizer.get_rand(), self.luck_lvl, min_q, max_q)
                items[count] = [Generator.create_item(item_type)] * quantity
            count += 1

        return items






