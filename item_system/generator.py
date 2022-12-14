
from item_system.item import Item
import json


class Generator:
    all_items_by_type = {}

    def __init__(self):
        with open("item_system/items.json", 'r') as file:
            Generator.all_items_by_type = json.loads(file.read())

    @classmethod
    def create_item(cls, item_type: bytes, item_id: int = None) -> Item:
        key = "type"
        item_dict = {}
        for i in range(len(cls.all_items_by_type)):
            if (key, item_type) in cls.all_items_by_type[i].items():
                item_dict = cls.all_items_by_type[i]
                break
        if item_dict:
            return Item(item_id=item_id,
                        item_type=item_dict['type'],
                        name=item_dict['name'],
                        rarity=item_dict['rarity'],
                        description=item_dict['description'],
                        value=item_dict['value'],
                        usable=item_dict['usable'],
                        consumable=item_dict['consumable'],
                        stackable=item_dict["stackable"],
                        img_url=item_dict['image_url'])

        else:
            print(f'Type {item_type} not found in items.')
            return None

    @classmethod
    def create_items(cls, lisr_type_id: []) -> []:
        list_items = []
        print(len(lisr_type_id))
        for i in range(len(lisr_type_id)):
            if len(lisr_type_id) > 1 and i % 2 == 0:
                list_items.append(cls.create_item(item_id=lisr_type_id[i], item_type=lisr_type_id[i+1]))

        return list_items

    @classmethod
    def to_list(cls, records) -> []:
        id_type_list = []
        for i in range(len(records)):
            for j in range(0, 2):
                id_type_list.append(records[i][j])
        return id_type_list
