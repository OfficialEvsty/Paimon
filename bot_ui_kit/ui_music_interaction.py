import discord
import music.custom_music
from discord.ui import Select, View


class UI_MusicView:
    def __init__(self, list_tracks: [], user_id):
        self.owner_id = user_id
        self.list_tracks = list_tracks



    def create_view(self) -> discord.ui.View:
        skip_track_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label="Skip",
            custom_id="Skip_Track"
        )

        pause_track_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label="Pause",
            custom_id="Pause_Track"
        )

        resume_track_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label="Unpause",
            custom_id="Unpause_Track"
        )

        async def on_skip_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                await music.custom_music.skip(interaction)
                return await interaction.response.send_message(f"Трек пропущен", delete_after=10)

        async def on_pause_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                await music.custom_music.pause(interaction)
                return await interaction.response.send_message(f"Трек поставлен на паузу", delete_after=10)

        async def on_resume_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                await music.custom_music.resume(interaction)
                return await interaction.response.send_message(f"Трек снят с паузы", delete_after=10)

        skip_track_button.callback = on_skip_callback
        pause_track_button.callback = on_pause_callback
        resume_track_button.callback = on_resume_callback
        #for i in range(len(self.list_namecards)):



        """async def on_action_item_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                if select_menu_2.values[0] == "Drop":
                    i = int(select_menu_1.values[0])
                    chosen_item = self.list_items[i]
                    await commands.cmd_inventory.drop(interaction, chosen_item)
                    await commands.cmd_inventory.show_inventory(interaction)
                elif select_menu_2.values[0] == "Use":
                    i = int(select_menu_1.values[0])
                    chosen_item = self.list_items[i]
                    await chosen_item.use(interaction, chosen_item)
                    await commands.cmd_inventory.show_inventory(interaction)
            else:
                await interaction.response.send_message("Это не ваш инвентарь, руки прочь!", delete_after=5)

        select_menu_2.callback = on_action_item_callback

        async def select_item_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                i = int(select_menu_1.values[0])
                select_menu_2.disabled = False
                view = discord.ui.View()
                view.add_item(select_menu_1)
                view.add_item(select_menu_2)
                await commands.cmd_inventory.draw_inventory_edit(interaction, self.list_items, i, view)
            else:
                await interaction.response.send_message("Не воруйте", delete_after=5)"""

        #select_menu_1.callback = select_item_callback


        view = discord.ui.View(timeout=None)
        view.add_item(skip_track_button)
        view.add_item(pause_track_button)
        view.add_item(resume_track_button)
        #.add_item(select_menu_2)
        return view

    def create_select_action(self) -> discord.ui.View:
        pass
