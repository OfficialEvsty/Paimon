from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json

class Inventory_GUI:
    def __init__(self, list_items: []):
        self.list_items = list_items
        file_to_open = "item_system/inventory_gui_settings.json"
        with open(file_to_open, "r") as file:
            self.cfg = json.loads(file.read())
        self.mode = self.cfg['mode']
        self.background_path = self.cfg['background_path']
        self.border_path = self.cfg['border_path']
        self.item_holder_size_k = self.cfg['item_holder_size_k']
        self.holder_paddings_k = self.cfg['holder_paddings_k']
        self.inventory_size_on_page = self.cfg['inventory_size_on_page']
        self.inventory_size_row = self.cfg['inventory_size_row']
        self.interval_btw_holders_k = self.cfg['interval_btw_holders_k']
        self.item_size_k = self.cfg['item_size_k']
        self.dict_stars = self.cfg['dict_stars']
        self.dict_rarity = self.cfg["rarity"]
        self.mask = self.cfg["mask"]
        self.chosen_img_size_k = self.cfg["chosen_img_size_k"]



    def draw(self, chosen_item: int = None) -> BytesIO:
        pass
        # Создаем бэкграунд
        im = Image.open(self.background_path).convert(self.mode)
        item_holder_with_border = Image.open(self.dict_rarity["default"]).convert(self.mode)
        border = Image.open(self.border_path).convert(self.mode)
        mask = Image.open(self.mask)

        (width, height) = im.size

        # Изменение размера ячейки


        resized_border = border.resize((int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))
        resized_ih_boreder = item_holder_with_border.resize((int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))

        (w_hold, h_hold) = resized_ih_boreder.size

        # Создаем кисть
        im_draw = ImageDraw.Draw(im)


        # Создаем ячейки
        counter = 0
        indent_w = self.holder_paddings_k[0] * width
        indent_h = self.holder_paddings_k[1] * height
        for i in range(self.inventory_size_on_page):
            """mask = Image.open(str(self.dict_rarity["default"]))
            resized_mask = mask.resize(
                (int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))"""

            if i < len(self.list_items):
                # Указываем путь соответствующей редкости
                item_holder = Image.open(str(self.dict_rarity[self.list_items[i].rarity]))
                """stars_count = Image.open(str(self.dict_rarity[self.list_items[i].rarity]))
                stars_count = stars_count.resize(item_holder.size)"""
                item_holder = item_holder.resize(
                    (int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))

                item_img = Image.open(self.list_items[i].img_url)
                resized_item_img = item_img.resize((int(width * self.item_holder_size_k[0]), int(width * self.item_holder_size_k[1])))
                item_holder.paste(item_holder, item_holder)
                item_holder.paste(resized_item_img, resized_item_img)
                """item_holder.paste(stars_count, stars_count)"""
                if chosen_item == i:
                    (w_item, h_item) = item_img.size
                    item_holder.paste(resized_border, resized_border)
                    im.paste(item_img, (int(width * self.chosen_img_size_k[0]) - w_item // 2, int(height * self.chosen_img_size_k[1]) - h_item // 2), item_img)
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


