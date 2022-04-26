import time

from discord.ext import commands
from discord import app_commands

class Basic(commands.Cog, name="basic"):
	"""
		Basic commands, like ping.
		
		Require intents: 
			- None
		
		Require bot permission:
			- send_messages
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str]:
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like ping."
		return emoji, label, description

	@commands.hybrid_command(name="ping", description="Ping the bot.")
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True)
	async def ping(self, ctx: commands.Context):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.send(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")



async def setup(bot):
	await bot.add_cog(Basic(bot))