import discord


class Custom_Embed:
    def construct(self, interaction: discord.Interaction, title: str, description: str, color:int = None, image_url: str = None, footer_text: str = None,
                  tumbnail_url: str = None) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
        ).set_author(
            name=interaction.user,
            icon_url=interaction.user.avatar
        ).set_image(
            url=image_url
        ).set_footer(
            text=footer_text
        ).set_thumbnail(
            url=tumbnail_url
        )

        return embed
