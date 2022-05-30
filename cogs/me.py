import discord

from discord.ext import commands
from discord import app_commands

@app_commands.guild_only()
class Me(commands.GroupCog, name="me", group_name="me", group_description="Like minecraft set your own /me !"):
	"""
		Like minecraft set your own /me !
	
		Require intents: 
			- None
		
		Require bot permission:
			- None
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '🤙'
		label = "Me"
		description = "Set and show a brief description of yourself."
		return emoji, label, description

	@app_commands.command(name="set", description="Set your own brief description of yourself !")
	@app_commands.describe(description="Your brief description of yourself.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def me(self, interaction: discord.Interaction, description: str):
		"""Allows you to set or show a brief description of yourself."""
		try:
			text = description.replace("'", "''")
			if max_lenght_me := self.subconfig_data["max_length"] < len(text) : 
				raise commands.CommandError(f"The max-lenght of your *me* is set to: __{max_lenght_me}__ (yours is {len(text)}).")
			
			await self.bot.database.insert_onduplicate(self.subconfig_data["table"], {"guild_id": interaction.guild_id, "user_id": interaction.user.id, "user_me": text})
			
			await self.show_me_message(interaction, interaction.user)
		except Exception as e:
			raise commands.CommandError(str(e))

	@app_commands.command(name="show", description="Show the /me of other users.")
	@app_commands.describe(user="The user you want to show the /me of.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def show_me(self, interaction: discord.Interaction, user: discord.Member = None):
		"""Allows you to show the description of other users."""
		if not user:
			user = interaction.user
		await self.show_me_message(interaction, user)

	async def show_me_message(self, interaction: discord.Interaction, user: discord.Member) -> None:
		response = await self.bot.database.lookup(self.subconfig_data["table"], "user_me", {"guild_id": str(user.guild.id),"user_id":  str(user.id)})
		message = " ".join(response[0]) if len(response) else "No description provided.."
		await interaction.response.send_message(f"• **{user.display_name}** {message}")



async def setup(bot):
	await bot.add_cog(Me(bot))
