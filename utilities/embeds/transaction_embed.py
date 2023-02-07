import discord
from utilities.emojis import Emoji


class Transaction_Embed(discord.Embed):
    def __init__(self, user: discord.User, reason: str, money: int = None, received_items: {} = None,
                 given_items: {} = None, date: str = None):
        super().__init__()
        self.title = f"Транзакция пользователя `{user}`.\nПричина: `{reason}`"
        self.set_author(name=user)
        self.set_thumbnail(url=user.avatar)
        title = f"Инвентарь `{user}`"
        output_received_items = "Добавлены:\n"
        output_given_items = "Удалены:\n"

        if money:
            if money < 0:
                self.add_field(name="Баланс", value=f"Потратил `{money}` {Emoji.Primogem}")
            else:
                self.add_field(name="Баланс", value=f"Заработал `{money}` {Emoji.Primogem}")
        if received_items:
            for items in received_items.values():
                output_received_items += f"`+` `{items[0].name}` : `x{len(items)}`\n"
            self.add_field(name=title, value=output_received_items)

        if given_items:
            for items in given_items.values():
                output_given_items += f"`-` `{items[0].name}` : `x{len(items)}` \n"
            self.add_field(name=title, value=output_given_items)

        if date is not None:
            self.set_footer(text=date)




