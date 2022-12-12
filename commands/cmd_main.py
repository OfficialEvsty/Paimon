from utilities.embeds.custom import Custom_Embed
import discord


async def create_custom_embed(interaction: discord.Interaction, title: str = None, description: str = None, color: int = None, image_url: str = None,
                              tumbnail: str = None) -> discord.Embed:
    custom_embed = Custom_Embed().construct(interaction=interaction, title=title, description=description, color=color, image_url=image_url, tumbnail_url=tumbnail)
    await interaction.response.send_message(embed=custom_embed)


async def show_tips(interaction: discord.Interaction):

    embed = discord.Embed(title="The best friendly tips to feel comfort here.", description="Click on button to transform me!")

    async def on_click_button_edit(inter):
        user = inter.user
        transform_button.disabled = True
        embed = discord.Embed(title="Thanks for responding.", description=f"{user} clicked on button.")
        await inter.message.edit(embed=embed)





    transform_button = discord.ui.Button(style=discord.ButtonStyle.primary, label="Кликай")
    transform_button.callback = on_click_button_edit
    selectoption = discord.SelectOption(label="Можешь выбрать", value=1, description="Тут должно быть описание")
    selectoption2 = discord.SelectOption(label="Тоже Можешь выбрать", value=2, description="Тут должно быть описание")
    selectmenu = discord.ui.Select(placeholder="Ждм клика", options=[selectoption2, selectoption])

    view = discord.ui.View()
    view.add_item(transform_button)
    #view.add_item(selectmenu)

    msg = await interaction.response.send_message(embed=embed, view=view)

