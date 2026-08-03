from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from discord import Interaction, SelectOption
from discord.ext import commands
from discord.ui import Select
from discord.utils import MISSING

from views.view import View as Parent


class CustomDropdown(Select):
    def __init__(
        self,
        placeholder: str,
        min_val: int,
        max_val: int,
        options: list[dict[str, str]],
        when_callback: Callable[..., Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_val,
            max_values=max_val,
            options=[
                SelectOption(
                    label=option["label"],
                    value=option.get("value", MISSING),
                    description=option.get("description"),
                    emoji=option.get("emoji"),
                    default=bool(option.get("default", False)),
                )
                for option in options
            ],
        )
        self.when_callback = when_callback

    async def callback(self, interaction: Interaction) -> None:
        await self.when_callback(self, interaction)


class View(Parent):
    """Standalone dropdown-only view."""

    def __init__(
        self,
        invoke: commands.Context | Interaction | None,
        placeholder: str,
        min_val: int,
        max_val: int,
        options: list[dict[str, str]],
        when_callback: Callable[..., Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__()

        self.invoke = invoke

        self.add_item(
            CustomDropdown(
                placeholder=placeholder,
                min_val=min_val,
                max_val=max_val,
                options=options,
                when_callback=when_callback,
            )
        )
