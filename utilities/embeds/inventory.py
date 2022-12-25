import discord


class Inventory_Embed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, description: str, image_url: str = None,
                  tumbnail_url: str = None) -> discord.Embed:
        super().__init__()
        self.title = f"Инвентарь пользователя `{interaction.user}`"
        self.description = description
        self.color = discord.Color.random()
        self.set_image(url=image_url)
        self.set_thumbnail(url=tumbnail_url)
        self.set_author(name=interaction.user, icon_url=interaction.user.avatar)
