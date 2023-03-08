import time

from discord.ext import commands

from classes.discordbot import DiscordBot
from classes.utilities import bot_has_permissions

class Basic(commands.Cog, name="basic"):
	"""
		Basic commands, like ping.
		
		Require intents: 
			- None
		
		Require bot permission:
			- send_messages
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like ping."
		return emoji, label, description

	@bot_has_permissions(send_messages=True)
	@commands.hybrid_command(name="ping", description="Ping the bot.")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def ping(self, ctx: commands.Context) -> None:
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.send(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")



async def setup(bot: DiscordBot):
	await bot.add_cog(Basic(bot))