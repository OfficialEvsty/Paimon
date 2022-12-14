import discord
from discord.ui import Select, View
import commands.cmd_inventory
import json

class UI_InventoryView():
    def __init__(self, list_items: [], user_id):
        self.owner_id = user_id
        self.list_items = list_items
        file_path = "bot_ui_kit/settings.json"
        with open(file_path, 'r') as file:
            self.cfg = json.loads(file.read())
        self.sel_menu_1_id = self.cfg['sel_menu_1_id']
        self.sel_menu_1_placeholder = self.cfg['sel_menu_1_placeholder']
        self.sel_menu_1_max_v = self.cfg['sel_menu_1_max_v']
        self.sel_menu_1_min_v = self.cfg['sel_menu_1_min_v']
        self.sel_menu_2_id = self.cfg['sel_menu_2_id']
        self.sel_menu_2_placeholder = self.cfg['sel_menu_2_placeholder']
        self.sel_menu_2_max_v = self.cfg['sel_menu_2_max_v']
        self.sel_menu_2_min_v = self.cfg['sel_menu_2_min_v']



    def create_select(self) -> discord.ui.View:
        select_menu_1 = discord.ui.Select(custom_id=self.sel_menu_1_id, placeholder=self.sel_menu_1_placeholder)
        select_menu_2 = discord.ui.Select(custom_id=self.sel_menu_1_id, placeholder=self.sel_menu_1_placeholder)


        for i in range(len(self.list_items)):
            select_menu_1.add_option(label=self.list_items[i].name, value=i, description=self.list_items[i].description)

        async def get_item_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                i = int(select_menu_1.values[0])
                chosen_item = self.list_items[i]
                await commands.cmd_inventory.draw_inventory_edit(interaction, self.list_items, i)
            else:
                await interaction.response.send_message("Не воруйте", delete_after=5)

        select_menu_1.callback = get_item_callback


        view = discord.ui.View()
        view.add_item(select_menu_1)
        return view


