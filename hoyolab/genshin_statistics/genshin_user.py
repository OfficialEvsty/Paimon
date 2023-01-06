from hoyolab.genshin_statistics.user_info import User_Info as UInfo
from hoyolab.genshin_statistics.abyss import Abyss
from hoyolab.hoyolab_user import Hoyolab
import genshin


class Genshin_User:
    def __init__(self, hoyolab: Hoyolab):
        cookies = hoyolab.cookies
        self.client = genshin.Client(cookies=cookies)
        self.user_info = None
        self.abyss = None

    async def init(self):
        self.user_info = UInfo(self.client)
        await self.user_info.init()
        self.abyss = Abyss(self.user_info)
        await self.abyss.init()

    def show(self) -> str:
        show_str = ""
        if self.user_info is not None:
            show_str += f"Игрок: {self.user_info.nickname}\nРегион: {self.user_info.region}" \
                        f"\nУровень: {self.user_info.level}\nUID: {self.user_info.uid}\n\n"

        if self.abyss is not None:
            show_str += f"Сезон: {self.abyss.season}\nНачало: {self.abyss.start_time}\n" \
                        f"Максимальный этаж: {self.abyss.max_floor}\nКоличество звёзд: {self.abyss.total_stars}\n" \
                        #f"Ранги: {self.abyss.ranks}"
        return show_str

