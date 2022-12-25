import discord


class Custom_Embed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, title: str, description: str, color:int = None, image_url: str = None,
                  tumbnail_url: str = None) -> discord.Embed:
        super().__init__()
        self.title = title
        self.description = description
        self.color = color
        self.set_image(url=image_url)
        self.set_thumbnail(url=tumbnail_url)
        self.set_author(name=interaction.user, icon_url=interaction.user.avatar)

