import discord
import functools

from typing import Union
from discord.ext import commands
from views.view import View as Parent

class CustomDropdown(discord.ui.Select):
    def __init__(self, placeholder : str, min_val : int, max_val : int, options: list[dict[str, str]], when_callback: functools.partial) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_val,
            max_values=max_val,
            options = 
                [
                    discord.SelectOption(
                        label=option["label"],
                        value=option.get("value", discord.utils.MISSING),
                        description=option.get("description", None),
                        emoji=option.get("emoji", None),
                        default=option.get("default", False), # type: ignore
                    ) 
                    for option in options
                ]
        )
        self.when_callback = when_callback

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.when_callback(self, interaction)

class View(Parent):
    """Dropdown View"""
    def __init__(self, invoke: Union[commands.Context, discord.Interaction, None], placeholder : str, min_val : int, max_val : int, options: list[dict[str, str]], when_callback) -> None:
        super().__init__()

        self.invoke = invoke

        self.add_item(
            CustomDropdown(
                placeholder=placeholder, 
                min_val=min_val,
                max_val=max_val,
                options=options,
                when_callback=when_callback
            )
        )
