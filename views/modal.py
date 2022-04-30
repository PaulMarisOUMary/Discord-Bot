import discord
import functools

from views.view import View as Parent

class CustomModal(discord.ui.Modal):
	def __init__(self, title: str, fields: dict[str, discord.ui.TextInput], when_submit: functools.partial):
		super().__init__(title=title)

		self.values : dict[str, str] = {}
		self.when_submit = when_submit

		self.__fields : dict[str, functools.partial] = {}
		for i, item in enumerate(fields.items()):
			key, value = item
			self.__fields[key] = functools.partial(self.__get_value, self.add_item(value).children[i])

	def __get_value(self, children: discord.ui.TextInput) -> str:
		return children.value

	async def on_submit(self, interaction: discord.Interaction):
		for key, value in self.__fields.items():
			self.values[key] = value()

		await self.when_submit(self, interaction)
		

class View(Parent):
	"""Button to Modal"""
	def __init__(self, source, label, style=discord.ButtonStyle.grey, emoji=None, disabled=False):
		super().__init__()

		async def when_submit(_class: CustomModal, interaction: discord.Interaction):
			formater = ''
			for key, value in _class.values.items():
				formater += f"\n`{key}`: `{value}`"

			await interaction.response.send_message(f"You submitted: {formater}")

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
				)
			},
			when_submit = when_submit
		)

		self.source = source
		self.button.label = label
		self.button.style = style
		self.button.emoji = emoji
		self.button.disabled = disabled

	async def button_func(self, interaction: discord.Interaction):
		if self.source.author != interaction.user:
			await interaction.response.send_message("You can't open this modal.", ephemeral=True)
		else:
			await interaction.response.send_modal(self.modal)

	@discord.ui.button(style = discord.ButtonStyle.blurple)
	async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.button_func(interaction)