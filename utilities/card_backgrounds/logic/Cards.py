import utilities.card_backgrounds
import os

cards_list = []
def init_cards_list(pattern: str = "_Card.jpg"):
    for file_name in os.listdir("utilities/card_backgrounds/"):
        if pattern in file_name:
            cards_list.append(file_name.replace(pattern, ""))