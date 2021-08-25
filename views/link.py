import discord

class View(discord.ui.View):
	"""Link View"""
	def __init__(self, label : str, url : str):
		super().__init__()

		self.add_item(discord.ui.Button(label=label, url=url))