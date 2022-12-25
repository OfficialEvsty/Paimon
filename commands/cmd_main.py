import utilities.embeds.custom
from utilities.embeds.custom import Custom_Embed
import discord


async def create_custom_embed(interaction: discord.Interaction) -> None:
    embed_modal = discord.ui.Modal(title="Конструктор Embed")
    title_input_box = discord.ui.TextInput(
        label="Заголовок",
        style=discord.TextStyle.short,
        max_length=128
    )

    desc_input_box = discord.ui.TextInput(
        label="Описание",
        style=discord.TextStyle.long,
        max_length=4000,
        required=False
    )

    img_url_input_box = discord.ui.TextInput(
        label="Ссылка на изображение",
        style=discord.TextStyle.short,
        required=False
    )

    tumbnail_url_input_box = discord.ui.TextInput(
        label="Ссылка на миниатюру",
        style=discord.TextStyle.short,
        required=False
    )

    color_digits_input_box = discord.ui.TextInput(
        label="Цвет(целое число)",
        style=discord.TextStyle.short,
        required=False
    )

    footer_input_box = discord.ui.TextInput(
        label="Нижний колонтитул",
        style=discord.TextStyle.short,
        required=False
    )

    embed_modal.add_item(title_input_box)
    embed_modal.add_item(desc_input_box)
    embed_modal.add_item(img_url_input_box)
    embed_modal.add_item(tumbnail_url_input_box)
    embed_modal.add_item(color_digits_input_box)

    async def on_custom_embed_submit(interaction: discord.Interaction):
        color = color_digits_input_box.value

        async def get_color(color) -> int:
            if not color == "":
                if color.isdigit():
                    return int(color)
                else:
                    return await interaction.response.send_message("Поле Цвет должно быть целым числом.",
                                                                   delete_after=5, ephemeral=True)
            else:
                return None

        embed = utilities.embeds.custom.Custom_Embed(
            interaction=interaction,
            title=title_input_box.value,
            description=desc_input_box.value,
            image_url=img_url_input_box.value,
            tumbnail_url=tumbnail_url_input_box.value,
            color=await get_color(color)
        )
        return await interaction.response.send_message(embed=embed)

    embed_modal.on_submit = on_custom_embed_submit


    await interaction.response.send_modal(embed_modal)


    """custom_embed = Custom_Embed().construct(interaction=interaction, title=title, description=description, color=color, image_url=image_url, tumbnail_url=tumbnail)
    return custom_embed"""


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

