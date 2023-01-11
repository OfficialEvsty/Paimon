from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json

class Inventory_GUI:
    def __init__(self, dict_items: {}, dict_items_to_trade: {} = None):
        self.__dict_items_to_trade__ = dict_items_to_trade
        self.__dict_items__ = dict_items
        file_to_open = "item_system/inventory_gui_settings.json"
        with open(file_to_open, "r") as file:
            self.cfg = json.loads(file.read())
        self.mode = self.cfg['mode']
        self.background_path = self.cfg['background_path']
        self.background_size = self.cfg['background_size']
        self.border_path = self.cfg['border_path']
        self.item_holder_size_k = self.cfg['item_holder_size_k']
        self.item_holder_size = (int(self.item_holder_size_k[0] * self.background_size[0]),
                                 int(self.item_holder_size_k[1] * self.background_size[0]))
        self.holder_paddings_k = self.cfg['holder_paddings_k']
        self.inventory_size_on_page = self.cfg['inventory_size_on_page']
        self.inventory_size_row = self.cfg['inventory_size_row']
        self.interval_btw_holders_k = self.cfg['interval_btw_holders_k']
        self.item_size_k = self.cfg['item_size_k']
        self.dict_stars = self.cfg['dict_stars']
        self.dict_rarity = self.cfg["rarity"]
        self.mask = self.cfg["mask"]
        self.chosen_img_pos_k = self.cfg["chosen_img_pos_k"]
        self.chosen_item_size_k = self.cfg["chosen_item_size_k"]

        holder_counter_paddings_k = self.cfg["holder_counter_paddings_k"]
        self.holder_counter_paddings = (int(self.item_holder_size[0] * holder_counter_paddings_k[0]),
                                        int(self.item_holder_size[1] * holder_counter_paddings_k[1]))

        # Trade
        self.panel_item_holders_size_k = self.cfg["panel_item_holders_size_k"]
        self.panel_item_holders_paddings_k = self.cfg["panel_item_holders_paddings_k"]
        self.panel_items_size = self.cfg["panel_items_size"]
        self.panel_interval_btw_holders_k = self.cfg["panel_interval_btw_holders_k"]

        self.font_path = self.cfg["font_path"]
        small_font_size = self.cfg["small_font_size"]
        self.small_font = ImageFont.truetype(font=self.font_path, size=small_font_size)


    def draw(self, chosen_item: int = None) -> BytesIO:
        pass
        # Создаем бэкграунд
        im = Image.open(self.background_path).convert(self.mode)
        item_holder_with_border = Image.open(self.dict_rarity["default"]).convert(self.mode)
        border = Image.open(self.border_path).convert(self.mode)

        (width, height) = im.size


        # Outdated

        if self.__dict_items_to_trade__ is not None:
            n = self.panel_items_size
            interval = int(self.panel_interval_btw_holders_k * width)
            holder_len = int(self.panel_item_holders_size_k * height)
            indent_w = (width - (n * holder_len + (n - 1) * interval)) // 2
            for i in range(self.panel_items_size):
                if i < len(self.__dict_items_to_trade__):
                    item_holder = Image.open(str(self.dict_rarity[self.__dict_items_to_trade__[i].rarity]))

                    item_holder = item_holder.resize(
                        (int(height * self.panel_item_holders_size_k), int(height * self.panel_item_holders_size_k)))


                    item_img = Image.open(self.__dict_items_to_trade__[i].img_url)
                    resized_item_img = item_img.resize(
                        (int(item_holder.width), int(item_holder.width)))
                    mask = resized_item_img.copy()
                    resized_item_img.putalpha(255)

                    item_holder.paste(im=resized_item_img, mask=mask)
                else:
                    item_holder = Image.open(str(self.dict_rarity["default"])).convert(self.mode)

                    item_holder = item_holder.resize(
                        (int(height * self.panel_item_holders_size_k),
                         int(height * self.panel_item_holders_size_k)))

                im.paste(item_holder, (int(indent_w), int(height * self.panel_item_holders_paddings_k[1])), item_holder)
                indent_w += item_holder.width + self.panel_interval_btw_holders_k * width




        # Изменение размера ячейки


        resized_border = border.resize((int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))
        resized_ih_boreder = item_holder_with_border.resize((int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))

        (w_hold, h_hold) = resized_ih_boreder.size

        # Создаем ячейки
        counter = 0
        indent_w = self.holder_paddings_k[0] * width
        indent_h = self.holder_paddings_k[1] * height
        for i in range(self.inventory_size_on_page):
            if i < len(self.__dict_items__):
                # Указываем путь соответствующей редкости
                item_holder = Image.open(str(self.dict_rarity[self.__dict_items__[i][0].rarity]))
                item_holder = item_holder.resize(
                    (int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))

                item_img = Image.open(self.__dict_items__[i][0].img_url)
                resized_item_img = item_img.resize((int(width * self.item_holder_size_k[0]),
                                                    int(width * self.item_holder_size_k[1])))

                mask = resized_item_img.copy()
                resized_item_img.putalpha(255)

                item_holder.paste(resized_item_img, mask)
                count = len(self.__dict_items__[i])
                if count > 1:
                    draw_holder = ImageDraw.Draw(item_holder)
                    draw_holder.text(xy=self.holder_counter_paddings, text=str(count), fill=(255, 255, 255),
                                     anchor="rs", font=self.small_font)
                if chosen_item == i:
                    resized_chosen_item_img = item_img.resize((int(width * self.chosen_item_size_k[0]), int(width * self.chosen_item_size_k[1])))
                    (w_item, h_item) = resized_chosen_item_img.size
                    item_holder.paste(resized_border, resized_border)
                    im.paste(resized_chosen_item_img, (int(width * self.chosen_img_pos_k[0]) - w_item // 2, int(height * self.chosen_img_pos_k[1]) - h_item // 2), resized_chosen_item_img)
            else:
                item_holder = Image.open(str(self.dict_rarity["default"])).convert(self.mode)

            item_holder = item_holder.resize(
                (int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))

            if counter != self.inventory_size_row:
                im.paste(item_holder, (int(indent_w), int(indent_h)), item_holder)
                indent_w += w_hold + self.interval_btw_holders_k[0] * width
            else:
                indent_w = self.holder_paddings_k[0] * width
                indent_h += h_hold + self.interval_btw_holders_k[1] * height
                im.paste(item_holder, (int(indent_w), int(indent_h)), item_holder)
                indent_w += w_hold + self.interval_btw_holders_k[0] * width
                counter = 1
                continue
            counter += 1



        # Добавляем нужной ячейки бордер
        #resized_ih_boreder.paste(resized_border, resized_border)

        # Накладываем ячейки на бэкграунд
        #im.paste(im=resized_ih_boreder, box=(int(width*self.holder_paddings_k[0]), int(height*self.holder_paddings_k[1])),mask=resized_ih_boreder)
        #Накладываем изображение предметов на ячейки

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)

        return buffer


