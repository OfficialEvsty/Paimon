from waifu_system.harem import Harem
from waifu_system.waifu import Waifu
from discord import Member


class HaremInteraction:
    def __init__(self, harem: Harem, index: int = None):
        self.harem = harem
        self.__index = 0
        if index:
            if index < len(self.harem.waifus):
                self.__index = index

            if len(self.harem.waifus) > 0:
                self.chosen: Waifu = self.harem.waifus[self.__index]
            else:
                self.chosen: Waifu = None
        else:
            self.choose_owner()

    def move(self, is_forward: bool):
        value = 1 if is_forward else -1
        self.__index += value

    def switch(self, index: int = None):
        if index is not None:
            index = index
        else:
            index = self.__index
        if len(self.harem.waifus) <= self.__index:
            return
        self.chosen = self.harem.waifus[index]

    def choose_owner(self):
        self.chosen: Waifu = self.harem.waifu_owner
