import item_system.item_use.usage
import random
from item_system.item import Item
import json


class Generator:
    all_items_by_type = {}

    def __init__(self):
        with open("item_system/items.json", 'r') as file:
            Generator.all_items_by_type = json.loads(file.read())

    @classmethod
    def generate_random_items_by_group_type(cls, group_type: str, count: int = 1) -> []:
        dicts_list_by_group_type = []
        for i in range(len(cls.all_items_by_type)):
            if ("group_type", group_type) in cls.all_items_by_type[i].items():
                dicts_list_by_group_type.append(cls.all_items_by_type[i])

        result_dicts_list = []
        max_len = len(dicts_list_by_group_type)
        for i in range(count):
            result_dicts_list.append(dicts_list_by_group_type[random.randint(0, max_len-1)])

        result_items_list = []
        for i in range(len(result_dicts_list)):
            item = Item(item_type=result_dicts_list[i]['type'],
                        name=result_dicts_list[i]['name'],
                        rarity=result_dicts_list[i]['rarity'],
                        description=result_dicts_list[i]['description'],
                        value=result_dicts_list[i]['value'],
                        usable=result_dicts_list[i]['usable'],
                        consumable=result_dicts_list[i]['consumable'],
                        stackable=result_dicts_list[i]["stackable"],
                        img_url=result_dicts_list[i]['image_url'])
            result_items_list.append(item)
        return result_items_list

    """@classmethod
    def generate_items_by_type(cls, item_type: int, count: int = 1) -> []:
        dicts_list_by_group_type = []
        for i in range(len(cls.all_items_by_type)):
            if ("group_type", group_type) in cls.all_items_by_type[i].items():
                dicts_list_by_group_type.append(cls.all_items_by_type[i])

        result_dicts_list = []
        max_len = len(dicts_list_by_group_type)
        for i in range(count):
            result_dicts_list.append(dicts_list_by_group_type[random.randint(0, max_len - 1)])

        result_items_list = []
        for i in range(len(result_dicts_list)):
            item = Item(item_type=result_dicts_list[i]['type'],
                        name=result_dicts_list[i]['name'],
                        rarity=result_dicts_list[i]['rarity'],
                        description=result_dicts_list[i]['description'],
                        value=result_dicts_list[i]['value'],
                        usable=result_dicts_list[i]['usable'],
                        consumable=result_dicts_list[i]['consumable'],
                        stackable=result_dicts_list[i]["stackable"],
                        img_url=result_dicts_list[i]['image_url'])
            result_items_list.append(item)
        return result_items_list"""

    @classmethod
    def create_item(cls, item_type: bytes, item_id: int = None) -> Item:
        key = "type"
        item_dict = {}
        for i in range(len(cls.all_items_by_type)):
            if (key, item_type) in cls.all_items_by_type[i].items():
                item_dict = cls.all_items_by_type[i]
                break
        if item_dict:
            item = Item(item_id=item_id,
                        item_type=item_dict['type'],
                        name=item_dict['name'],
                        rarity=item_dict['rarity'],
                        description=item_dict['description'],
                        value=item_dict['value'],
                        usable=item_dict['usable'],
                        consumable=item_dict['consumable'],
                        stackable=item_dict["stackable"],
                        img_url=item_dict['image_url'])

            for (func_name, func) in item_system.item_use.usage.usage_functions_dict.items():
                if func_name == item_dict['group_type']:
                    print(f"{func_name} : {func}")
                    item.use = item_system.item_use.usage.usable(func)

            return item


        else:
            print(f'Type {item_type} not found in items.')
            return None

    # specific for only db interactive
    @classmethod
    def create_items(cls, list_type_id: []) -> []:
        list_items = []
        for i in range(len(list_type_id)):
            if len(list_type_id) > 1 and i % 2 == 0:
                list_items.append(cls.create_item(item_id=list_type_id[i], item_type=list_type_id[i + 1]))

        return list_items

    @classmethod
    def create_items_without_id(cls, list_type_id: []) -> []:
        list_items = []
        for i in range(len(list_type_id)):
            list_items.append(cls.create_item(item_type=list_type_id[i]))
        return list_items

    @classmethod
    def to_list(cls, records) -> []:
        id_type_list = []
        for i in range(len(records)):
            for j in range(0, 2):
                id_type_list.append(records[i][j])
        return id_type_list
