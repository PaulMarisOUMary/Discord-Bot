from __future__ import annotations

import operator
from collections.abc import Callable, Coroutine
from typing import Any

from discord import ButtonStyle, Embed, Interaction
from discord.ext import commands
from discord.ui import Button as dButton

from utils.basetypes import CommandLike, HasHelpCustom
from utils.helpengine import HelpEngine
from views.dropdown import CustomDropdown
from views.view import View as Parent


class Button(dButton):
    def __init__(
        self,
        context: commands.Context,
        label: str,
        style: ButtonStyle,
        when_callback: Callable[..., Coroutine[Any, Any, None]],
        argument: Any | None,
    ) -> None:
        disabled = argument in (-1, 0)

        self.when_callback = when_callback
        self.invoker = context.author
        self.argument = argument

        super().__init__(style=style, label=label, disabled=disabled)

    async def callback(self, interaction: Interaction) -> None:
        if self.invoker.id == interaction.user.id:
            await self.when_callback(interaction, self.argument)
        else:
            await interaction.response.send_message(
                ":x: Hey it's not your session !", ephemeral=True
            )


class View(Parent):
    def __init__(
        self,
        *,
        timeout: float | None = 300,
        mapping: dict[commands.Cog | None, list[CommandLike]],
        engine: HelpEngine,
        home_embed: Embed,
    ) -> None:
        super().__init__(timeout=timeout)

        self.context = engine.ctx
        self.bot = self.context.bot
        self.home_embed = home_embed
        self.engine = engine
        self.cogs: list[commands.Cog | None] = [None]
        self.index = 0
        self.buttons: list[dButton] = []
        self.options: list[dict[str, str]] = [
            {
                "label": "Home",
                "description": "Show the home page.",
                "emoji": '👋',
                "value": "home_page",
            }
        ]

        for cog in mapping:
            if isinstance(cog, HasHelpCustom):
                self.cogs.append(cog)

        self.cogs[1:] = sorted(self.cogs[1:], key=operator.attrgetter("qualified_name"))

        self.add_dropdown()
        self.add_buttons()

    def add_dropdown(self) -> None:
        async def on_select(dropdown: CustomDropdown, interaction: Interaction) -> None:
            if self.context.author.id != interaction.user.id:
                await interaction.response.send_message(
                    ":x: Hey it's not your session !", ephemeral=True
                )
                return

            cog_name = dropdown.values[0]
            if cog_name == "home_page":
                await self.to_embed(interaction, 0)
                return

            cog = self.bot.get_cog(cog_name)
            index = self.cogs.index(cog, 1)
            await self.to_embed(interaction, index)

        for cog in self.cogs[1:]:
            if not isinstance(cog, HasHelpCustom):
                continue

            emoji, label, description = cog.help_custom()
            self.options.append(
                {
                    "label": label,
                    "description": description,
                    "emoji": emoji,
                    "value": cog.qualified_name,
                }
            )

        self.add_item(
            CustomDropdown(
                placeholder="Select a category...",
                min_val=1,
                max_val=1,
                options=self.options,
                when_callback=on_select,
            )
        )

    def add_buttons(self) -> None:
        buttons_property = [
            ("<<", ButtonStyle.grey, self.to_embed, 0),
            ("Back", ButtonStyle.blurple, self.to_embed, -1),
            ("Next", ButtonStyle.blurple, self.to_embed, -2),
            (">>", ButtonStyle.grey, self.to_embed, len(self.options) - 1),
            ("Quit", ButtonStyle.red, self.quit, None),
        ]

        for label, style, command, argument in buttons_property:
            button = Button(
                context=self.context,
                label=label,
                style=style,
                when_callback=command,
                argument=argument,
            )
            self.buttons.append(button)
            self.add_item(button)

    async def to_embed(self, interaction: Interaction, index: int) -> None:
        if index == -1:
            self.index += index
        elif index == -2:
            self.index += 1
        else:
            self.index = index

        for button in self.buttons[:-1]:
            button.disabled = False

        if self.index == len(self.options) - 1:
            for button in self.buttons[2:4]:
                button.disabled = True

        if self.index == 0:
            embed = self.home_embed
            for button in self.buttons[:2]:
                button.disabled = True
        else:
            cog = self.cogs[self.index]
            assert cog is not None
            embed = await self.engine.build_cog_embed(cog)

        await interaction.response.edit_message(embed=embed, view=self)

    async def quit(self, interaction: Interaction, *_args: Any) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
