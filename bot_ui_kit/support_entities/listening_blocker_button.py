from discord.ui import Button
from discord import Interaction, User
from discord import ButtonStyle
import asyncio

# This class encapsulate list of users,
# who pushed the button once and should waiting when button's callback would process.


class ListeningBlocker:
    def __init__(self):
        pass
    # ubl - The list of users to block listening.
    ubl = []

    # This method add user in ubl.
    @classmethod
    def add_listener_in_ubl(cls, user: User):
        user_id = user.id
        if user_id not in cls.ubl:
            cls.ubl.append(user_id)

    # This method removes user from ubl.
    @classmethod
    def remove_listener_from_ubl(cls, user: User):
        user_id = user.id
        if user_id in cls.ubl:
            cls.ubl.remove(user_id)

    # This method checks if user in ubl.
    @classmethod
    def is_listener_in_ubl(cls, user: User):
        user_id = user.id
        if user_id in cls.ubl:
            return True
        return False

    # Decorator for button's callback functions. It tracks users who waiting for end of button's responding
    @classmethod
    def add_to_listening_blocker(cls, func):
        async def wrapper(obj, interaction: Interaction):
            user = interaction.user
            if cls.is_listener_in_ubl(user):
                return await interaction.user.send("Помедленнее, куда вы спешите?")
            else:
                cls.add_listener_in_ubl(user)
                result = await func(obj, interaction)
            if result is None:
                cls.remove_listener_from_ubl(user)
        return wrapper



