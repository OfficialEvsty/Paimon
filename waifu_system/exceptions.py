from discord import Member


class InteractingNotOwner(Exception):
    def __init__(self, owner_id: int, interacting_id: int):
        super().__init__()
        self.txt = f"{interacting_id} is not owner of waifu. True owner is {owner_id}."


class OwnerDoesNotExist(Exception):
    def __init__(self, waifu: Member):
        super().__init__()
        self.txt = f"Owner of waifu: {waifu} doesn't exist."


class WaifuNotFound(Exception):
    def __init__(self, waifu_id: int):
        self.txt = f"Waifu ID: {waifu_id} not found."
