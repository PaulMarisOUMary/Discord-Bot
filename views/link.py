import discord

from views.view import View as Parent

class View(Parent):
	"""Link View"""
	def __init__(self, label: str, url: str) -> None:
		super().__init__()

		self.add_item(discord.ui.Button(label=label, url=url))