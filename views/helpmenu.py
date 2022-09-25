import discord
import functools

from discord import app_commands
from discord.ext import commands
from typing import Any, Optional, Union

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
	def __init__(self, 
	timeout: Optional[float], 
	context: commands.Context, 
	mapping: dict[Optional[commands.Cog], list[Union[commands.Command, app_commands.Command]]],
	homeembed: discord.Embed,
	ui: Optional[int]
	):
		super().__init__(timeout=timeout)

		self.mapping = mapping
		self.ctx = context
		self.index = 0
		self.embeds = [homeembed]
		self.options: list[dict[str, str]] = [
			{
				"label":"Home", 
				"description":"Show the home page.", 
				"emoji":'👋'
			}
		]
		self.gen_embeds()

		self.buttons: list[Button] = [] # First, Back, Next, End, Quit

		if ui == 0:
			self.add_dropdown()
		elif ui == 1:
			self.add_buttons
		else:
			self.add_dropdown()
			self.add_buttons()

	def add_buttons(self) -> None:
		buttonStyle = discord.ButtonStyle

		buttons_property = [
			("<<", buttonStyle.grey, self.set_page, 0),
			("Back", buttonStyle.blurple, self.to_page, -1),
			("Next", buttonStyle.blurple, self.to_page, +1),
			(">>", buttonStyle.grey, self.set_page, len(self.options)-1),
			("Quit", buttonStyle.red, self.quit, None)
		]

		for label, style, command, argument in buttons_property:
			button = Button(
				self.ctx,
				label=label,
				style=style,
				when_callback=command,
				argument=argument,
			)
			self.buttons.append(button)
			self.add_item(button)

	def add_dropdown(self) -> None:
		async def on_select(_class, interaction: discord.Interaction):
			if _class.view.ctx.author.id == interaction.user.id:
				index = _class.view.find_index_from_dropdown(_class.values[0])
				if not index:
					index = 0
				await _class.view.set_page(interaction, index)
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

	def get_cogs(self) -> list[commands.Cog]:
		return [cog for cog in self.mapping.keys() if cog is not None]

	def gen_embeds(self):
		for cog in self.get_cogs():
			if hasattr(cog, "help_custom") and cog in self.mapping:
				emoji, label, description = cog.help_custom() # type: ignore
				self.options.append(
					{
						"label":label,
						"description":description,
						"emoji":emoji,
					}
				)

				embed = discord.Embed(
					title = f"{emoji} Help · {label} ({len(self.mapping[cog])})",
					description=f"{cog.__doc__.lstrip(' ') if cog.__doc__ else None}",
					url="https://github.com/PaulMarisOUMary/Discord-Bot"
				)
				embed.set_footer(
					text="Remind : Hooks such as <> must not be used when executing commands.", 
					icon_url=self.ctx.message.author.display_avatar.url
				)

				def dig_parent(command, seen: Optional[list[str]] = None):
					if not seen:
						seen = [command.name]
					if command.parent:
						seen.append(command.parent.name)
						dig_parent(command.parent, seen)
					return seen

				for command in self.mapping[cog]:
					params = ""
					if isinstance(command, commands.Command):
						help = command.help
						name = f"{self.ctx.clean_prefix}{command.name}"
						for param in command.clean_params: 
							params += f" <{param}>"
					else:
						help = command.description
						name = "</"+' '.join(dig_parent(command)[::-1])+":01234567890123456789>"
						for param in command._params.keys():
							params += f" <{param}>"
					embed.add_field(
						name=f"{name}{params}",
						value=f"{help}\n\u200b",
						inline=False
					)
				self.embeds.append(embed)

	def find_index_from_dropdown(self, value: str):
		i = 0
		for cog in self.get_cogs():
			if hasattr(cog, "help_custom"):
				_, label, _ = cog.help_custom() # type: ignore
				if label == value: return i+1
				i += 1

	async def set_page(self, interaction: discord.Interaction, page: int):
		self.index = page
		await self.to_page(interaction, 0)

	async def to_page(self, interaction: discord.Interaction, page: int):
		if not self.index + page < 0 or not self.index + page > len(self.options):
			await self.set_index(page)
			embed = self.embeds[self.index]

			await interaction.response.edit_message(embed=embed, view=self)

	async def set_index(self, page: int):
		self.index += page
		if self.buttons:
			for button in self.buttons[0:-1]:
				button.disabled = False
			if self.index == 0: 
				for button in self.buttons[0:2]:
					button.disabled = True
			elif self.index == len(self.options)-1: 
				for button in self.buttons[2:4]:
					button.disabled = True

	async def quit(self, interaction: discord.Interaction, *args: Any):
		await interaction.response.defer()
		await interaction.delete_original_response()
		self.stop()