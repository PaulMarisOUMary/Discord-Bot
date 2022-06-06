import asyncio
import discord

from discord.ext import commands

from classes.discordbot import DiscordBot

class Status(commands.Cog, name="status"):
	"""A loop to set the current status of the bot."""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	"""def help_custom(self) -> tuple[str]:
		emoji = '🏷️'
		label = "Status"
		description = "Setup the status of the bot."
		return emoji, label, description"""

	async def cog_load(self):
		self.task_change_status = self.bot.loop.create_task(self.loop_change_status())

	async def cog_unload(self):
		self.task_change_status.cancel()

	async def loop_change_status(self) -> None:
		await self.bot.wait_until_ready()
		subconfig_data = self.bot.config["cogs"][self.__cog_name__.lower()]
		while not self.bot.is_closed():
			for status in subconfig_data["status"]:
				await self.bot.change_presence(
					activity=discord.Streaming(
						name=status, 
						url="https://www.twitch.tv/warriormachine_"), 
					status=discord.Status.do_not_disturb
				)
				await asyncio.sleep(subconfig_data["cooldown"])



async def setup(bot: DiscordBot):
	await bot.add_cog(Status(bot))