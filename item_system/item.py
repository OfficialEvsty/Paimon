

class Item:
    def __init__(self, item_id: int, item_type: bytes, name: str, description: str, value: int, usable: bool, consumable: bool,
                 stackable: bool,
                 img_url: str = None):
        self.id = item_id
        self.type = item_type
        self.name = name
        self.description = description
        self.value = value
        self.usable = usable
        self.consumable = consumable
        self.stackable = stackable
        self.img_url = img_url


