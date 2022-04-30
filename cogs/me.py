import discord

from discord.ext import commands
from discord import app_commands

class Me(commands.Cog, name="me"):
	"""
		Like minecraft set your own /me !
	
		Require intents: 
			- None
		
		Require bot permission:
			- None
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.me_data = self.bot.config["database"]["me"]
		self.max_lenght_me = self.me_data["max_length"]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '🤙'
		label = "Me"
		description = "Set and show a brief description of yourself."
		return emoji, label, description

	@app_commands.command(name="me", description="Set your own brief description of yourself !")
	@app_commands.describe(description="Your brief description of yourself.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def me(self, interaction: discord.Interaction, description: str):
		"""Allows you to set or show a brief description of yourself."""
		try:
			text = description.replace("'", "''")
			if len(text) > self.max_lenght_me: 
				raise commands.CommandError(f"The max-lenght of your *me* is set to: __{self.max_lenght_me}__ (yours is {len(text)}).")
			# Insert
			await self.bot.database.insert(self.me_data["table"], {"user_id": interaction.user.id, "user_me": text})
			# Update
			await self.bot.database.update(self.me_data["table"], "user_me", text, f"user_id = {interaction.user.id}")
			await self.show_me_message(interaction, interaction.user)
		except Exception as e:
			raise commands.CommandError(str(e))

	@app_commands.command(name="showme", description="Show the /me of other users.")
	@app_commands.describe(user="The user you want to show the /me of.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def show_me(self, interaction: discord.Interaction, user: discord.Member = None):
		"""Allows you to show the description of other users."""
		if not user:
			user = interaction.user
		await self.show_me_message(interaction, user)

	async def show_me_message(self, interaction: discord.Interaction, user: discord.Member) -> None:
		response = await self.bot.database.lookup(self.me_data["table"], "user_me", "user_id", str(user.id))
		message = " ".join(response[0]) if len(response) else "No description provided.."
		await interaction.response.send_message(f"• **{user.display_name}** {message}")



async def setup(bot):
	await bot.add_cog(Me(bot))
