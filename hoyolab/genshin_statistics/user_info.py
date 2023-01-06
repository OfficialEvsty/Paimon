import genshin


class User_Info:
    def __init__(self, client: genshin.Client):
        self.client = client
        self.uid = None
        self.level = None
        self.nickname = None
        self.region = client.region.value

        self.user_card_genshin = None

    async def init(self):
        cards = await self.client.get_record_cards(self.client.hoyolab_id, lang="ru-ru")
        for card in cards:
            if card.game is genshin.Game.GENSHIN:
                self.user_card_genshin = card
            self.level = self.user_card_genshin.level
            self.nickname = self.user_card_genshin.nickname
            self.uid = self.user_card_genshin.uid
