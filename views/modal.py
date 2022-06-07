import discord
import functools

from typing import Union
from discord.ext import commands
from views.view import View as Parent

class CustomModal(discord.ui.Modal):
	def __init__(self, title: str, fields: dict[str, Union[discord.ui.TextInput, discord.ui.Select]], when_submit: functools.partial):
		super().__init__(title=title)

		self.values : dict[str, str] = {}
		self.when_submit = when_submit

		self.__fields : dict[str, functools.partial] = {}
		for i, item in enumerate(fields.items()):
			key, value = item
			self.__fields[key] = functools.partial(self.__get_value, self.add_item(value).children[i])

	def __get_value(self, children: Union[discord.ui.TextInput, discord.ui.Select]) -> str:
		try:
			return children.value
		except AttributeError:
			return children.values
		except Exception as e:
			raise e

	async def on_submit(self, interaction: discord.Interaction):
		for key, value in self.__fields.items():
			self.values[key] = value()

		await self.when_submit(self, interaction)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		interaction.client.dispatch("modal_error", interaction, error)

class View(Parent):
	"""Button to Modal"""
	def __init__(self, invoke: Union[commands.Context, discord.Interaction] = None):
		super().__init__()

		self.invoker = invoke.author

		async def when_submit(_class: CustomModal, interaction: discord.Interaction):
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
				"mood": discord.ui.Select(
					placeholder="Mood (required)",
					min_values=1,
					max_values=5,
					options=[
						discord.SelectOption(label="Happy", value='😁', emoji='😁'),
						discord.SelectOption(label="Good", value='😊', emoji='😊'),
						discord.SelectOption(label="Neutral", value='😐', emoji='😐'),
						discord.SelectOption(label="Sad", value='😢', emoji='😢'),
						discord.SelectOption(label="Angry", value='😡', emoji='😡'),
					],
					disabled=False # Must be False, else the user will not be able to send the modal
				)
			},
			when_submit = when_submit
		)

	@discord.ui.button(label = "Sample modal", style = discord.ButtonStyle.gray, emoji = '📧')
	async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.invoker != interaction.user:
			await interaction.response.send_message("You can't open this modal.", ephemeral=True)
		else:
			await interaction.response.send_modal(self.modal)