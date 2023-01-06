from hoyolab.genshin_statistics.user_info import User_Info as UInfo


class Abyss:
    def __init__(self, user_info: UInfo):
        self.user_info = user_info
        self.max_floor = None
        self.ranks = None
        self.total_stars = None
        self.start_time = None
        self.season = None

    async def init(self):
        spiral_abyss_data = await self.user_info.client.get_genshin_spiral_abyss(uid=self.user_info.uid, lang="ru-ru")
        self.max_floor = spiral_abyss_data.max_floor
        self.ranks = spiral_abyss_data.ranks
        self.total_stars = spiral_abyss_data.total_stars
        self.start_time = spiral_abyss_data.start_time
        self.season = spiral_abyss_data.season
