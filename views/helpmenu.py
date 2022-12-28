import discord
import functools

from discord import app_commands, ButtonStyle
from discord.ext import commands
from typing import Any, Dict, List, Optional, Union

from views.dropdown import CustomDropdown
from views.view import View as Parent

class Button(discord.ui.Button):
	def __init__(self,
        context: commands.Context,
        label: str,
        style: discord.ButtonStyle,
        when_callback: functools.partial,
        argument: Optional[Any],
	):
		disabled = False
		if argument == -1 or argument == 0:
			disabled = True
		self.when_callback = when_callback
		self.invoker = context.author
		self.argument = argument

		super().__init__(style=style, label=label, disabled=disabled)

	async def callback(self, interaction: discord.Interaction):
		if self.invoker.id == interaction.user.id:
			await self.when_callback(interaction, self.argument)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(Parent):
    def __init__(self, *,
        timeout: Optional[float] = 300,
        mapping: Dict[Optional[commands.Cog], Union[List[commands.Command], List[app_commands.Command], List[commands.HybridCommand]]],
        help_object: commands.HelpCommand,
        home_embed: discord.Embed,
    ):
        super().__init__(timeout=timeout)

        self.context = help_object.context
        self.bot = self.context.bot
        self.home_embed = home_embed
        self.help_class = help_object
        self.cogs: List[Optional[commands.Cog]] = [None]
        self.index = 0
        self.buttons: List[discord.ui.Button] = []
        self.options: List[Dict[str, str]] = [
            {
                "label": "Home",
                "description": "Show the home page.",
                "emoji": '👋',
                "value": "home_page"
            }
        ]
        for cog in mapping:
            if not cog:
                continue
            if hasattr(cog, "help_custom"):
                emoji, label, description = cog.help_custom() # type: ignore

                self.options.append(
                    {
                        "label": label,
                        "description": description,
                        "emoji": emoji,
                        "value": cog.qualified_name,
                    }
                )
                self.cogs.append(cog)

        self.add_dropdown()
        self.add_buttons()

    def add_dropdown(self):
        async def on_select(_class, interaction: discord.Interaction):
            if self.context.author.id == interaction.user.id:
                cog_name = _class.values[0]
                if cog_name == "home_page":
                    embed = self.home_embed
                else:
                    cog = self.bot.get_cog(cog_name)
                    embed = await self.help_class.send_cog_help(cog, view_invoked=True) # type: ignore
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

        self.add_item(
            CustomDropdown(
                placeholder="Select a category...",
                min_val=1,
                max_val=1,
                options=self.options,
                when_callback=on_select # type: ignore
            )
        )

    def add_buttons(self):
        buttons_property = [
			("<<", ButtonStyle.grey, self.to_embed, 0),
			("Back", ButtonStyle.blurple, self.to_embed, -1),
			("Next", ButtonStyle.blurple, self.to_embed, +1),
			(">>", ButtonStyle.grey, self.to_embed, len(self.options)-1),
			("Quit", ButtonStyle.red, self.quit, None)
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

    async def to_embed(self, interaction: discord.Interaction, index: int):
        if index == 1 or index == -1:
            self.index += index
        else:
            self.index = index

        for button in self.buttons[0:-1]:
            button.disabled = False

        if self.index == len(self.options)-1:
            for button in self.buttons[2:4]:
                button.disabled = True

        if self.index == 0:
            embed = self.home_embed
            for button in self.buttons[0:2]:
                button.disabled = True
        else:
            cog = self.cogs[self.index]
            embed = await self.help_class.send_cog_help(cog, view_invoked=True) # type: ignore

        await interaction.response.edit_message(embed=embed, view=self)

    async def quit(self, interaction: discord.Interaction, *args: Any):
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()