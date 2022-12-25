import discord
from item_system.inventory import Inventory


usage_functions_dict = {}


def add_item_use(func_usage):
    usage_functions_dict[func_usage.__name__] = func_usage
    print(usage_functions_dict)
    def on_use(interaction: discord.Interaction, item):
        func_usage(interaction, item)

    return on_use

# Decorator
def usable(func_usage):
    async def on_use(interaction: discord.Interaction, item):
        if item.usable:
            await func_usage(interaction, item)
            if item.consumable:
                await Inventory.remove_item(interaction, item.id)
                print(f"{item.name} успешно использован и потрачен.")
        else:
            print("Предмет не является используемым.")

    return on_use