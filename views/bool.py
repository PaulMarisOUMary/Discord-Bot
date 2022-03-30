import discord

class View(discord.ui.View):
	"""Bool View"""
	def __init__(self, source, flabel = "Confirm", slabel = "Cancel", femoji = "✅", semoji= "🚫", fdisabled = False, sdisable = False, fstyle = discord.ButtonStyle.green, sstyle = discord.ButtonStyle.grey, emojis = True):
		super().__init__()
		self.source = source
		self.invoker = source.author
		self.value = None
		self.confirm.label, self.cancel.label = flabel, slabel
		self.confirm.disabled, self.cancel.disabled = fdisabled, sdisable
		self.confirm.style, self.cancel.style = fstyle, sstyle

		if emojis: self.confirm.emoji, self.cancel.emoji = femoji, semoji

	async def bool_check(self, value, interaction):
		if self.invoker == interaction.user:
			self.value = value
			await interaction.response.defer()
			await interaction.delete_original_message()
			message = "✅ Confirmed" if self.value else "❌ Canceled"
			await self.source.reply(message)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

	@discord.ui.button(style = discord.ButtonStyle.blurple)
	async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.bool_check(True, interaction)

	@discord.ui.button(style = discord.ButtonStyle.blurple)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.bool_check(False, interaction)