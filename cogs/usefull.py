from typing import List
import discord

from discord.ext import commands
from discord import app_commands

class Usefull(commands.Cog, name="usefull"):
	"""Usefull commands for Devs & more."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	"""def help_custom(self) -> tuple[str]:
		emoji = '🚩'
		label = "Usefull"
		description = "Usefull commands."
		return emoji, label, description"""

	@app_commands.command(name="strawpoll", description="Create a strawpoll.")
	@app_commands.describe(question="The question of the strawpoll.")
	@app_commands.guilds(discord.Object(id=332234497078853644))
	async def avatar(self, interaction: discord.Interaction, question: str):
		await interaction.response.send_message(content=f"__*{interaction.user.mention}*__ : {question}", allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False))
		message = await interaction.original_message()
		await message.add_reaction("<a:checkmark_a:842800730049871892>")
		await message.add_reaction("<a:crossmark:842800737221607474>")



async def setup(bot):
	await bot.add_cog(Usefull(bot))
