import discord
import logging

from classes.discordbot import DiscordBot
from classes.utilities import load_config, clean_close, cogs_manager, set_logging, cogs_directory

from os import listdir

class Bot(DiscordBot):
	def __init__(self, **kwargs) -> None:
		super().__init__(
			activity = discord.Game(name = "Booting.."),
			allowed_mentions=discord.AllowedMentions(everyone=False),
			case_insensitive = True,
			config = kwargs.pop("config", load_config()), # custom kwarg
			intents = kwargs.pop("intents", discord.Intents.all()),
			max_messages = 2500,
			status = discord.Status.idle,
			**kwargs,
		)

	async def startup(self) -> None:
		"""Sync application commands"""
		await self.wait_until_ready()
		
		# Sync application commands
		synced = await self.tree.sync()
		self.log(message = f"Application commands synced ({len(synced)})", name = "discord.startup")
		
	async def setup_hook(self) -> None:
		"""Initialize the bot, database, prefixes & cogs."""
		await super().setup_hook()

		# Cogs loader
		cogs = [f"cogs.{filename[:-3]}" for filename in listdir(cogs_directory) if filename.endswith(".py")]
		await cogs_manager(self, "load", cogs)
		self.log(message = f"Cogs loaded ({len(cogs)}): {', '.join(cogs)}", name = "discord.setup_hook")

		# Sync application commands
		self.loop.create_task(self.startup())

if __name__ == '__main__':
	clean_close() # Avoid Windows EventLoopPolicy Error

	bot = Bot(
		intents = discord.Intents(
			emojis = True,
			guild_scheduled_events = True,
			guilds = True,
			invites = True,
			members = True,
			message_content = True,
			messages = True,
			presences = True,
			reactions = True,
			voice_states = True,
		),
	)
	bot.logger, streamHandler = set_logging(file_level = logging.INFO, console_level = logging.INFO, filename = "discord.log")
	bot.run(
		bot.config["bot"]["token"],
		reconnect = True,
		log_handler = streamHandler,
		log_level = logging.DEBUG, # Must be set to DEBUG, change the log_level of each handler in set_logging() method
	)