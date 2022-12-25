import discord


class Item:
    def __init__(self, item_type: bytes, name: str, rarity: str, description: str, value: int,
                 usable: bool,
                 consumable: bool,
                 stackable: bool,
                 img_url: str = None,
                 item_id: int = None):
        self.id = item_id
        self.type = item_type
        self.name = name
        self.rarity = rarity
        self.description = description
        self.value = value
        self.usable = usable
        self.consumable = consumable
        self.stackable = stackable
        self.img_url = img_url








