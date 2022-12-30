import discord
from discord.ui import View
from discord.ui import Select, View
import commands.cmd_inventory
import json


class UI_InventoryView:
    def __init__(self, inventory, user_id):
        self.owner_id = user_id
        self.inventory = inventory
        file_path = "bot_ui_kit/settings.json"
        with open(file_path, 'r') as file:
            self.cfg = json.loads(file.read())
        self.sel_menu_1_id = self.cfg['sel_menu_1_id']
        self.sel_menu_1_placeholder = self.cfg['sel_menu_1_placeholder']
        self.sel_menu_1_max_v = self.cfg['sel_menu_1_max_v']
        self.sel_menu_1_min_v = self.cfg['sel_menu_1_min_v']

        self.left_arrow_button = discord.ui.Button(style=discord.ButtonStyle.gray, disabled=True, emoji="◀️")
        self.right_arrow_button = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="▶️")
        self.accept_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Accept")
        self.revert_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Revert")
        self.close_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Close")
        if len(self.inventory.list_items_on_page) < self.inventory.page_size or \
                len(inventory.list_items) < self.inventory.page_size + 1:
            self.right_arrow_button.disabled = True
        self.use_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Use")
        self.drop_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Drop")

        self.timeout = None


    def create_custom_view(self) -> discord.ui.View:
        view = discord.ui.View(timeout=self.timeout)
        return view

    def create_select(self) -> discord.ui.View:

        trade_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Trade")

        select_menu_1 = discord.ui.Select(custom_id=self.sel_menu_1_id, placeholder=self.sel_menu_1_placeholder)


        for i in range(len(self.inventory.list_items_on_page)):
            select_menu_1.add_option(label=self.inventory.list_items_on_page[i].name, value=str(i), description=self.inventory.list_items_on_page[i].description)


        async def on_use_button(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                i = int(select_menu_1.values[0])
                chosen_item = self.inventory.list_items_on_page[i]
                if chosen_item.usable:
                    await chosen_item.use(interaction, chosen_item)
                    await commands.cmd_inventory.show_inventory(interaction, is_private=True)
                    await interaction.response.send_message(
                        f"{chosen_item.name} успешно использован игроком {interaction.user}.", delete_after=5,
                        ephemeral=True)

        self.use_button.callback = on_use_button

        async def on_drop_button(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                i = int(select_menu_1.values[0])
                chosen_item = self.inventory.list_items_on_page[i]
                await commands.cmd_inventory.drop(interaction, chosen_item)
                await commands.cmd_inventory.show_inventory(interaction, is_private=True)
                await interaction.response.defer()
                await interaction.followup.send(f"{chosen_item.name} выброшен из инвентаря {interaction.user}",
                                                delete_after=5, ephemeral=True)

        self.drop_button.callback = on_drop_button

        async def on_accept_callback(interaction: discord.Interaction):
            async def on_submit_cost(interaction: discord.Interaction):
                value = input_money_box.value
                timer = input_timer_box.value
                min_timer = 180
                if value.isdigit():
                    if (timer.isdigit() and int(timer) >= min_timer) or timer == "":
                        if timer == "":
                            timer = min_timer
                        else:
                            timer = int(timer)
                        if int(value) < 0:
                            value = abs(int(value))
                        await commands.cmd_inventory.trade(interaction, self.inventory, value, timer)
                        await commands.cmd_inventory.show_inventory(interaction, True)
                    else:
                        await interaction.response.send_message("Значение поля `время` должно быть числовым и не меньше, чем 3 минуты(180).", delete_after=5, ephemeral=True)
                else:
                    await interaction.response.send_message("Значение поля `цена` должно быть числовым типом.", delete_after=5, ephemeral=True)

            if self.owner_id == interaction.user.id:
                if len(self.inventory.items_to_trade) == 0:
                    await interaction.response.send_message("Поместите в трейд лист предметы, чтобы выставить его на продажу.", delete_after=5, ephemeral=True)
                modal_money_to_cost = discord.ui.Modal(title="Установить цену для трейда")
                input_money_box = discord.ui.TextInput(label="Цена", style=discord.TextStyle.short, default="0", required=True)
                input_timer_box = discord.ui.TextInput(label="Укажите время жизни трейда", max_length=4, placeholder="Время в секундах", style=discord.TextStyle.short,
                                                       required=False)
                modal_money_to_cost.add_item(input_money_box)
                modal_money_to_cost.add_item(input_timer_box)
                modal_money_to_cost.on_submit = on_submit_cost
                await interaction.response.send_modal(modal_money_to_cost)


        self.accept_button.callback = on_accept_callback

        async def on_revert_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                await commands.cmd_inventory.show_inventory(interaction, True)

        self.revert_button.callback = on_revert_callback

        async def on_close_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                msg_id = interaction.message.id
                await interaction.response.defer()
                if msg_id is not None:
                    await interaction.delete_original_response()

        self.close_button.callback = on_close_callback

        async def on_right_arrow_clicked(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                is_active_button = await commands.cmd_inventory.switch_page(self.inventory, True)
                self.right_arrow_button.disabled = not is_active_button
                self.left_arrow_button.disabled = False

                select_menu_1.options.clear()

                for i in range(len(self.inventory.list_items_on_page)):
                    select_menu_1.add_option(
                        label=self.inventory.list_items_on_page[i].name,
                        value=str(i)
                    )

                view = self.create_custom_view()
                view.add_item(self.left_arrow_button)
                view.add_item(trade_button)
                view.add_item(self.close_button)
                view.add_item(self.right_arrow_button)
                view.add_item(select_menu_1)
                await commands.cmd_inventory.on_switch_page_select(interaction, view, self.inventory)

        self.right_arrow_button.callback = on_right_arrow_clicked

        async def on_left_arrow_clicked(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                is_active_button = await commands.cmd_inventory.switch_page(self.inventory, False)
                self.left_arrow_button.disabled = not is_active_button
                self.right_arrow_button.disabled = False

                select_menu_1.options.clear()

                for i in range(len(self.inventory.list_items_on_page)):
                    select_menu_1.add_option(
                        label=self.inventory.list_items_on_page[i].name,
                        value=str(i)
                    )
                view = self.create_custom_view()
                view.add_item(self.left_arrow_button)
                view.add_item(trade_button)
                view.add_item(self.close_button)
                view.add_item(self.right_arrow_button)
                view.add_item(select_menu_1)
                await commands.cmd_inventory.on_switch_page_select(interaction, view, self.inventory)

        self.left_arrow_button.callback = on_left_arrow_clicked

        async def on_trade_button_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                view = discord.ui.View()
                select_menu_offer = discord.ui.Select(
                    max_values=len(self.inventory.list_items_on_page)
                )
                for i in range(len(self.inventory.list_items_on_page)):
                    select_menu_offer.add_option(
                        label=self.inventory.list_items_on_page[i].name,
                        value=str(i)
                    )

                async def on_right_arrow_clicked(interaction: discord.Interaction):
                    if self.owner_id == interaction.user.id:
                        is_active_button = await commands.cmd_inventory.switch_page(self.inventory, True)
                        self.right_arrow_button.disabled = not is_active_button
                        self.left_arrow_button.disabled = False
                        self.list_items = self.inventory.list_items_on_page

                        async def on_trade_items_selected(interactions: discord.Interaction):
                            items_for_trade_list = []
                            items_in_inventory = self.inventory.list_items_on_page.copy()
                            for i in range(len(select_menu_offer.values)):
                                print(f"list_index: {i} , select: {int(select_menu_offer.values[i])}")
                                item = self.inventory.list_items_on_page[int(select_menu_offer.values[i])]
                                items_for_trade_list.append(item)
                                items_in_inventory.remove(item)

                            view = self.create_custom_view()
                            print(len(self.inventory.list_items_on_page))
                            is_right_but_valid = await self.inventory.add_items_to_trade(items_for_trade_list)
                            if await self.inventory.is_page_empty():
                                items_in_inventory = self.inventory.list_items_on_page

                            print(len(self.inventory.list_items_on_page))
                            select_menu_offer.options.clear()

                            select_menu_offer.max_values = len(self.inventory.list_items_on_page)
                            for i in range(len(self.inventory.list_items_on_page)):
                                select_menu_offer.add_option(
                                    label=self.inventory.list_items_on_page[i].name,
                                    value=str(i)
                                )
                            select_menu_offer.callback = on_trade_items_selected


                            view.remove_item(self.right_arrow_button)
                            self.right_arrow_button.disabled = not is_right_but_valid
                            self.left_arrow_button.disabled = not self.inventory.left_button_check()
                            view.add_item(self.left_arrow_button)
                            view.add_item(self.accept_button)
                            view.add_item(self.revert_button)
                            view.add_item(self.right_arrow_button)
                            view.add_item(select_menu_offer)
                            if len(self.inventory.list_items) == 0:
                                view.remove_item(select_menu_offer)
                            await commands.cmd_inventory.show_trade_inventory(interactions, view, items_in_inventory,
                                                                              items_for_trade_list, self.inventory)
                        select_menu_offer = discord.ui.Select(
                            max_values=len(self.list_items)
                        )
                        select_menu_offer.callback = on_trade_items_selected

                        for i in range(len(self.list_items)):
                            select_menu_offer.add_option(
                                label=self.list_items[i].name,
                                value=str(i)
                            )
                        view = self.create_custom_view()
                        view.add_item(self.left_arrow_button)
                        view.add_item(self.accept_button)
                        view.add_item(self.revert_button)
                        view.add_item(self.right_arrow_button)
                        view.add_item(select_menu_offer)
                        await commands.cmd_inventory.on_switch_page(interaction, self.list_items, view, self.inventory)


                self.right_arrow_button.callback = on_right_arrow_clicked


                async def on_left_arrow_clicked(interaction: discord.Interaction):
                    if self.owner_id == interaction.user.id:
                        is_active_button = await commands.cmd_inventory.switch_page(self.inventory, False)
                        self.left_arrow_button.disabled = not is_active_button
                        print(is_active_button)
                        self.right_arrow_button.disabled = False
                        self.list_items = self.inventory.list_items_on_page
                        print(len(self.list_items))

                        async def on_trade_items_selected(interactions: discord.Interaction):
                            items_for_trade_list = []
                            items_in_inventory = self.inventory.list_items_on_page.copy()
                            for i in range(len(select_menu_offer.values)):
                                print(f"list_index: {i} , select: {int(select_menu_offer.values[i])}")
                                item = self.inventory.list_items_on_page[int(select_menu_offer.values[i])]
                                items_for_trade_list.append(item)
                                items_in_inventory.remove(item)

                            view = discord.ui.View()
                            print(len(self.inventory.list_items_on_page))
                            is_right_but_valid = await self.inventory.add_items_to_trade(items_for_trade_list)
                            if await self.inventory.is_page_empty():
                                items_in_inventory = self.inventory.list_items_on_page

                            print(len(self.inventory.list_items_on_page))
                            select_menu_offer.options.clear()

                            select_menu_offer.max_values = len(self.inventory.list_items_on_page)
                            for i in range(len(self.inventory.list_items_on_page)):
                                print(f"{i} : {self.inventory.list_items_on_page[i].name}")
                                select_menu_offer.add_option(
                                    label=self.inventory.list_items_on_page[i].name,
                                    value=str(i)
                                )
                            select_menu_offer.callback = on_trade_items_selected

                            view.remove_item(self.right_arrow_button)
                            self.right_arrow_button.disabled = not is_right_but_valid
                            self.left_arrow_button.disabled = not self.inventory.left_button_check()
                            view.add_item(self.left_arrow_button)
                            view.add_item(self.accept_button)
                            view.add_item(self.revert_button)
                            view.add_item(self.right_arrow_button)
                            view.add_item(select_menu_offer)
                            if len(self.inventory.list_items) == 0:
                                view.remove_item(select_menu_offer)
                            await commands.cmd_inventory.show_trade_inventory(interactions, view, items_in_inventory,
                                                                              items_for_trade_list, self.inventory)

                        select_menu_offer = discord.ui.Select(

                            max_values=len(self.list_items)
                        )
                        select_menu_offer.callback = on_trade_items_selected

                        for i in range(len(self.list_items)):
                            select_menu_offer.add_option(
                                label=self.list_items[i].name,
                                value=str(i)
                            )
                        view = self.create_custom_view()
                        view.add_item(self.left_arrow_button)
                        view.add_item(self.accept_button)
                        view.add_item(self.revert_button)
                        view.add_item(self.right_arrow_button)
                        view.add_item(select_menu_offer)
                        await commands.cmd_inventory.on_switch_page(interaction, self.list_items, view, self.inventory)

                self.left_arrow_button.callback = on_left_arrow_clicked


                async def on_trade_items_selected(interactions: discord.Interaction):
                    items_for_trade_list = []
                    items_in_inventory = self.inventory.list_items_on_page.copy()
                    for i in range(len(select_menu_offer.values)):
                        print(f"list_index: {i} , select: {int(select_menu_offer.values[i])}")
                        item = self.inventory.list_items_on_page[int(select_menu_offer.values[i])]
                        items_for_trade_list.append(item)
                        items_in_inventory.remove(item)

                    view = self.create_custom_view()
                    print(len(self.inventory.list_items_on_page))
                    is_right_but_valid = await self.inventory.add_items_to_trade(items_for_trade_list)
                    if await self.inventory.is_page_empty():
                        items_in_inventory = self.inventory.list_items_on_page

                    print(len(self.inventory.list_items_on_page))
                    select_menu_offer.options.clear()

                    select_menu_offer.max_values = len(self.inventory.list_items_on_page)
                    for i in range(len(self.inventory.list_items_on_page)):
                        print(f"{i} : {self.inventory.list_items_on_page[i].name}")
                        select_menu_offer.add_option(
                            label=self.inventory.list_items_on_page[i].name,
                            value=str(i)
                        )
                    select_menu_offer.callback = on_trade_items_selected

                    view.remove_item(self.right_arrow_button)
                    self.right_arrow_button.disabled = not is_right_but_valid
                    self.left_arrow_button.disabled = not self.inventory.left_button_check()
                    view.add_item(self.left_arrow_button)
                    view.add_item(self.accept_button)
                    view.add_item(self.revert_button)
                    view.add_item(self.right_arrow_button)
                    view.add_item(select_menu_offer)
                    if len(self.inventory.list_items) == 0:
                        view.remove_item(select_menu_offer)
                    await commands.cmd_inventory.show_trade_inventory(interactions, view, items_in_inventory,
                                                                      items_for_trade_list, self.inventory)

                select_menu_offer.callback = on_trade_items_selected

                view.add_item(self.left_arrow_button)
                view.add_item(self.accept_button)
                view.add_item(self.revert_button)
                view.add_item(self.right_arrow_button)
                view.add_item(select_menu_offer)
                if len(self.inventory.list_items) == 0:
                    view.remove_item(select_menu_offer)
                await commands.cmd_inventory.show_trade_inventory(interaction, view, inventory=self.inventory)

        trade_button.callback = on_trade_button_callback

        async def select_item_callback(interaction: discord.Interaction):
            if self.owner_id == interaction.user.id:
                i = int(select_menu_1.values[0])
                chosen_item = self.inventory.list_items_on_page[i]
                self.use_button.disabled = not chosen_item.usable
                view = self.create_custom_view()
                view.add_item(self.left_arrow_button)
                view.add_item(self.use_button)
                view.add_item(self.drop_button)
                view.add_item(self.close_button)
                view.add_item(self.right_arrow_button)
                view.add_item(select_menu_1)
                await commands.cmd_inventory.draw_inventory_edit(interaction, self.inventory.list_items_on_page, i, view)
            else:
                await interaction.response.send_message("Не воруйте", delete_after=5)

        select_menu_1.callback = select_item_callback


        view = self.create_custom_view()
        view.add_item(self.left_arrow_button)
        view.add_item(trade_button)
        view.add_item(self.close_button)
        view.add_item(self.right_arrow_button)
        view.add_item(select_menu_1)

        return view



