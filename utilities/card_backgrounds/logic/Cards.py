import utilities.card_backgrounds
import os

cards_list = []
format_file = '.png'


def init_cards_list(pattern: str = f"_Card{format_file}"):
    for file_name in os.listdir("utilities/card_backgrounds/"):
        if pattern in file_name:
            cards_list.append(file_name.replace(pattern, ""))