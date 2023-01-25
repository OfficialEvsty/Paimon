from discord import Embed


class GiftEmbed(Embed):
    def __init__(self, gift):
        super().__init__()
        self.owner = gift.owner
        self.id = gift.id
        self.timer = gift.timer
        self.title = f"⎢Подарок №`{self.id}` от пользователя `{self.owner}`"
        self.description = f"Подарок истечёт через `{self.timer // 60}` минут(ы), если вы его не заберете."
        self.set_author(name=self.owner, icon_url=self.owner.avatar)