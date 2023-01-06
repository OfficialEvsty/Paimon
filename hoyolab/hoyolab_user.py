import genshin
import genshin.client.components.hoyolab


class Hoyolab:
    def __init__(self, cookies: {}):
        self.cookies = cookies
        self.client = genshin.Client(self.cookies)
        self.user: genshin.client.components.hoyolab.base.hoyolab_models.FullHoyolabUser = None

    async def init(self):
        self.user = await self.client.get_hoyolab_user(self.cookies["ltuid"])
