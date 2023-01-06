import discord
import genshin
from utilities.emojis import Emoji


class UI_HoyolabView:
    def __init__(self, user: discord.User, hoyolab):
        self.owner = user
        self.owner_id = user.id
        self.hoyolab = hoyolab

    async def create_view(self) -> discord.ui.View:

        daily_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            emoji=Emoji.Daily
        )

        async def on_dayly_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                await interaction.response.defer()
                result_str = await get_daily(hoyolab=self.hoyolab)
                await interaction.followup.send(result_str)

        daily_button.callback = on_dayly_callback

        close_profile_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Close",
            custom_id="Close_Button"
        )

        async def on_close_callback(interaction: discord.Interaction):

            if self.owner_id == interaction.user.id or interaction.message.interaction.user.id == interaction.user.id:
                msg = interaction.message
                if msg is not None:
                    await interaction.message.delete()
                    return await interaction.response.send_message("Спасибо, что поддерживаете чат в чистоте", delete_after=5, ephemeral=True)
            else:
                await interaction.response.send_message("Вы не можете закрыть чужой профиль.", delete_after=5,
                                                   ephemeral=True)

        close_profile_button.callback = on_close_callback

        view = discord.ui.View()
        view.add_item(daily_button)
        view.add_item(close_profile_button)

        return view


async def get_daily(hoyolab) -> str:
    try:
        reward = await hoyolab.client.claim_daily_reward(game=genshin.Game.GENSHIN, lang="ru-ru")
    except genshin.AlreadyClaimed:
        return "Ежедневная награда уже получена"
    else:
        return f"Получено {reward.amount} {reward.name}"
