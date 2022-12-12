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
        self.item_holder_path = self.cfg['item_holder_path']
        self.border_path = self.cfg['border_path']
        self.item_holder_size_k = self.cfg['item_holder_size_k']
        self.holder_paddings_k = self.cfg['holder_paddings_k']
        self.inventory_size_on_page = self.cfg['inventory_size_on_page']
        self.inventory_size_row = self.cfg['inventory_size_row']
        self.interval_btw_holders_k = self.cfg['interval_btw_holders_k']
        self.item_size_k = self.cfg['item_size_k']



    def draw(self, inventory_size = 10) -> BytesIO:
        pass
        # Создаем бэкграунд
        im = Image.open(self.background_path).convert(self.mode)
        item_holder_with_border = Image.open(self.item_holder_path).convert(self.mode)
        item_holder = Image.open(self.item_holder_path).convert(self.mode)
        border = Image.open(self.border_path).convert(self.mode)

        (width, height) = im.size

        # Изменение размера ячейки


        resized_border = border.resize((int(width * self.item_holder_size_k[0]), int(height * self.item_holder_size_k[1])))
        resized_ih_boreder = item_holder_with_border.resize((int(width * self.item_holder_size_k[0]), int(height * self.item_holder_size_k[1])))
        resized_ih_boreder.putalpha(128)

        (w_hold, h_hold) = resized_ih_boreder.size

        # Создаем кисть
        im_draw = ImageDraw.Draw(im)


        # Создаем ячейки
        counter = 0
        indent_w = self.holder_paddings_k[0] * width
        indent_h = self.holder_paddings_k[1] * height
        for i in range(inventory_size):
            item_holder = Image.open(self.item_holder_path)
            item_holder = item_holder.resize(
                (int(width * self.item_holder_size_k[0]), int(height * self.item_holder_size_k[1])))

            if i < len(self.list_items):
                item_img = Image.open(self.list_items[i].img_url)
                resized_item_img = item_img.resize((int(w_hold * self.item_size_k[0]), int(h_hold * self.item_size_k[1])))
                item_holder.paste(resized_item_img, resized_item_img)

            if counter != self.inventory_size_row:
                im.paste(item_holder, (int(indent_w), int(indent_h)), item_holder)
                indent_w += w_hold + self.interval_btw_holders_k[0] * width
            else:
                indent_w = self.holder_paddings_k[0] * width
                indent_h += h_hold + self.interval_btw_holders_k[1] * height
                im.paste(item_holder, (int(indent_w), int(indent_h)), item_holder)
                counter = 0
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


