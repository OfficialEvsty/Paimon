import discord
from discord.ui import Select, View
import commands.cmd_inventory
import commands.cmd_profile


class UI_ProfileView:
    def __init__(self, list_namecards: [] = None, user_id = None):
        self.owner_id = user_id
        self.list_namecards = list_namecards
        self.profile_timeout = None



    def create_view(self) -> discord.ui.View:
        edit_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label="Edit",
            custom_id="Edit"
        )

        close_profile_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Close",
            custom_id="Close_Button"
        )

        back_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Back",
            custom_id="Back_Button"
        )

        async def on_back_button(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                view = discord.ui.View()
                view.add_item(edit_button)
                view.add_item(close_profile_button)
                await commands.cmd_profile.cmd_edit_view(interaction, view)

        back_button.callback = on_back_button


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


        async def on_edit_callback(interactions: discord.Interaction):
            if self.owner_id == interactions.user.id:

                edit_namecard_button = discord.ui.Button(
                    style=discord.ButtonStyle.gray,
                    label="Card",
                    custom_id="Edit_Card"
                )

                edit_bio_button = discord.ui.Button(
                    style=discord.ButtonStyle.gray,
                    label="Bio",
                    custom_id="Edit_Bio"
                )

                edit_uid_button = discord.ui.Button(
                    style=discord.ButtonStyle.gray,
                    label="UID",
                    custom_id="Edit_UID"
                )

                edit_namecard_button.callback = on_edit_namecard
                edit_bio_button.callback = on_edit_bio
                edit_uid_button.callback = on_edit_uid
                view = discord.ui.View()
                view.add_item(edit_namecard_button)
                view.add_item(edit_bio_button)
                view.add_item(edit_uid_button)
                view.add_item(back_button)
                view.timeout = self.profile_timeout
                await commands.cmd_profile.cmd_edit_view(interactions, view)
            else:
                await interactions.response.send_message("Вы не можете редактировать чужой профиль.", delete_after=5, ephemeral=True)

        edit_button.callback = on_edit_callback

        async def on_edit_bio(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                input_box = discord.ui.TextInput(
                    label="Опишите себя",
                    style=discord.TextStyle.long,
                    default="Default Bio as you wished.",
                    max_length=100,
                    custom_id="Text_Input_Bio",
                )

                async def on_inputed_bio(interaction: discord.Interaction):
                    if self.owner_id == interaction.user.id:
                        await commands.cmd_profile.cmd_set_or_update_bio(interaction, input_box.value)
                        await commands.cmd_profile.cmd_card(interaction)

                view = discord.ui.Modal(title="Добавьте информацию о себе")
                view.add_item(input_box)
                view.on_submit = on_inputed_bio
                view.timeout = self.profile_timeout
                await interaction.response.send_modal(view)

        async def on_edit_uid(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                input_box = discord.ui.TextInput(
                    label="Введите Ваш UID в игре",
                    style=discord.TextStyle.short,
                    max_length=9,
                    custom_id="Text_Input_UID",
                )

                async def on_inputed_uid(interaction: discord.Interaction):
                    if self.owner_id == interaction.user.id:
                        await commands.cmd_profile.cmd_set_or_update_uid(interaction, input_box.value)
                        await commands.cmd_profile.cmd_card(interaction)

                view = discord.ui.Modal(title="Регистрация UID")
                view.add_item(input_box)
                view.on_submit = on_inputed_uid
                view.timeout = self.profile_timeout
                await interaction.response.send_modal(view)



        async def on_edit_namecard(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                cards_list = await commands.cmd_profile.cmd_get_user_cards(interaction)
                select_menu_cards = discord.ui.Select()
                for i in range(len(cards_list)):
                    select_menu_cards.add_option(label=cards_list[i], value=i, description="")

                async def on_selected_card(interaction: discord.Interaction):
                    if self.owner_id == interaction.user.id:
                        index = int(select_menu_cards.values[0])
                        print(type(cards_list))

                        chosen_card = cards_list[index]
                        await commands.cmd_profile.cmd_update_user_namecard(interaction, chosen_card)
                        await commands.cmd_profile.cmd_card(interaction)

                select_menu_cards.callback = on_selected_card

                view = discord.ui.View()
                view.add_item(select_menu_cards)
                view.timeout = self.profile_timeout
                await commands.cmd_profile.cmd_edit_view(interaction, view)


        view = discord.ui.View()
        view.add_item(edit_button)
        view.add_item(close_profile_button)
        view.timeout = self.profile_timeout
        return view

