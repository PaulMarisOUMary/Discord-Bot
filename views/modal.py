import discord
import functools

from typing import Callable, Union
from discord.ext import commands

from views.view import View as Parent

Children = Union[discord.ui.TextInput, discord.ui.Select]

class CustomModal(discord.ui.Modal):
	children: list[Children]

	def __init__(self, title: str, fields: dict[str, Children], when_submit: Callable) -> None:
		super().__init__(title=title)

		self.values : dict[str, str] = {}
		self.when_submit = when_submit

		self.__fields : dict[str, Callable] = {}
		for i, item in enumerate(fields.items()):
			key, value = item
			self.__fields[key] = functools.partial(self.__get_value, self.add_item(value).children[i])

	def __get_value(self, children: Children) -> Union[str, list[str]]:
		if isinstance(children, discord.ui.TextInput):
			return children.value
		elif isinstance(children, discord.ui.Select):
			return children.values
		elif isinstance(children, discord.ui.Label):
			return self.__get_value(children.component)
		else:
			raise TypeError(f"Invalid type for children: {type(children)}")

	async def on_submit(self, interaction: discord.Interaction) -> None:
		for key, value in self.__fields.items():
			self.values[key] = value()

		await self.when_submit(self, interaction)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		interaction.client.dispatch("modal_error", interaction, error)

class View(Parent):
	"""Button to Modal"""
	def __init__(self, invoke: commands.Context) -> None:
		super().__init__()

		self.invoker = invoke.author

		async def when_submit(_class: CustomModal, interaction: discord.Interaction) -> None:
			formater = ''
			for key, value in _class.values.items():
				if isinstance(value, list):
					formater += f"\n{key}: {', '.join(value)}"
				else:
					formater += f"\n{key}: {value}"

			await interaction.response.send_message(f"__You submitted__ **:** {formater}")

		self.modal = CustomModal(
			title = "Custom Modal",
			fields = {
				"name": discord.ui.TextInput(
					label = "Name (required)",
					placeholder = "Your name here...",
					style = discord.TextStyle.short,
					required = True,
					min_length = 3
				),
				"feedback": discord.ui.TextInput(
					label = "Feedback (optional)",
					placeholder = "Your feedback here...",
					style = discord.TextStyle.long,
					required = False,
					min_length = 5,
					max_length = 300
				),
				"mood": discord.ui.Label(
					text="Your current mood",
					description="test",
					component=discord.ui.Select(
						placeholder="Mood (required)",
						min_values=1,
						max_values=3,
						required=True,
						options=[
							discord.SelectOption(label="Happy", value='😁', emoji='😁'),
							discord.SelectOption(label="Good", value='😊', emoji='😊'),
							discord.SelectOption(label="Neutral", value='😐', emoji='😐'),
							discord.SelectOption(label="Sad", value='😢', emoji='😢'),
							discord.SelectOption(label="Angry", value='😡', emoji='😡'),
						],
					),
				),
			},
			when_submit = when_submit
		)

	@discord.ui.button(label = "Sample modal", style = discord.ButtonStyle.gray, emoji = '📧')
	async def button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		if self.invoker != interaction.user:
			await interaction.response.send_message("You can't open this modal.", ephemeral=True)
		else:
			await interaction.response.send_modal(self.modal)