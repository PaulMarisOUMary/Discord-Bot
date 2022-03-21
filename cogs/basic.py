import time
from tkinter import NONE

from discord.ext import commands

class Basic(commands.Cog, name="basic"):
	"""Basic commands, like ping."""
	def __init__(self, bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str]:
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like ping."
		return emoji, label, description

	@commands.command(name="ping")
	async def ping(self, ctx):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.message.reply(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

def setup(bot):
	bot.add_cog(Basic(bot))
