import discord

from views.view import View as Parent

class SampleModal(discord.ui.Modal, title="Sample Modal"):
	name = discord.ui.TextInput(
		label = "Name (required)",
		placeholder = "Your name here...",
		required = True,
		min_length = 3
	)

	feedback = discord.ui.TextInput(
		label = "What do you think of this new feature?",
		placeholder = "Type your feedback here...",
		style = discord.TextStyle.long,
		required = False,
		max_length = 300
	)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.send_message(f"Thanks for your feedback, `{self.name.value}` !\n{self.feedback.value}", ephemeral=True)

	async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)


class View(Parent):
	"""Button to Modal"""
	def __init__(self, source, label, style=discord.ButtonStyle.grey, emoji=None, disabled=False):
		super().__init__()
		self.source = source
		self.button.label = label
		self.button.style = style
		self.button.emoji = emoji
		self.button.disabled = disabled

	async def button_func(self, interaction: discord.Interaction):
		if self.source.author != interaction.user:
			await interaction.response.send_message("You can't open this modal.", ephemeral=True)
		else:
			await interaction.response.send_modal(SampleModal())

	@discord.ui.button(style = discord.ButtonStyle.blurple)
	async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.button_func(interaction)