import discord

from discord.ext import commands, tasks

from classes.discordbot import DiscordBot

class Status(commands.Cog, name="status"):
	"""A loop to set the current status of the bot."""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot
		self.subconfig_data = self.bot.config["cogs"][self.__cog_name__.lower()]

		self.count = 0

	"""def help_custom(self) -> tuple[str]:
		emoji = '🏷️'
		label = "Status"
		description = "Setup the status of the bot."
		return emoji, label, description"""

	async def cog_load(self) -> None:
		self.task_change_status.change_interval(seconds=self.subconfig_data["cooldown"])
		self.task_change_status.start()

	async def cog_unload(self) -> None:
		self.task_change_status.cancel()

	@tasks.loop()
	async def task_change_status(self) -> None:
		await self.bot.wait_until_ready()

		await self.bot.change_presence(
			activity=discord.CustomActivity(
				name=self.subconfig_data["status"][self.count],
				emoji=None # Not supported (yet) by discord
			), 
			status=discord.Status.do_not_disturb
		)

		self.count = (self.count + 1) % len(self.subconfig_data["status"])



async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Status(bot))