import time
import discord

from discord.ext import commands
from discord import app_commands

class Basic(commands.Cog, name="basic"):
	"""Basic commands, like ping."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	"""def help_custom(self) -> tuple[str]:
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like ping."
		return emoji, label, description"""

	@app_commands.command(name="ping", description="Ping the bot.")
	@app_commands.guilds(discord.Object(id=332234497078853644))
	async def ping(self, interaction: discord.Interaction):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		await interaction.response.send_message(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await interaction.edit_original_message(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

async def setup(bot):
	await bot.add_cog(Basic(bot))
