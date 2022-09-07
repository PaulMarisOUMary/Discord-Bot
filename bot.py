import discord
import logging

from classes.database import DataSQL
from classes.discordbot import DiscordBot
from classes.utilities import load_config, clean_close, cogs_manager, set_logging, cogs_directory

from os import listdir
from discord.ext import commands

class Bot(DiscordBot):
	def __init__(self):
		super().__init__(
			allowed_mentions=discord.AllowedMentions(everyone=False),
			case_insensitive = True, 
			command_prefix = self.__prefix_callable, 
			intents = discord.Intents.all(),
			max_messages=2500,
		)

	def __prefix_callable(self, client: DiscordBot, message: discord.Message):
		if message.guild is None:
			return commands.when_mentioned_or(self.config["bot"]["default_prefix"])(client, message)

		guild_id = message.guild.id
		if guild_id in client.prefixes: 
			prefix = client.prefixes[guild_id]
		else: 
			prefix = self.config["bot"]["default_prefix"]
		return commands.when_mentioned_or(prefix)(client, message)

	async def on_ready(self):
		self.logger.name = "discord.on_ready"
		self.logger.info(msg=f"Logged as: {self.user} | discord.py{discord.__version__} Guilds: {len(self.guilds)} Users: {len(self.users)} Config: {len(self.config)}")

	async def close(self):
		self.logger.name = "discord.close"

		await self.database.close()
		self.logger.info(msg="Database connection closed")

		await super().close()

	async def startup(self):
		"""Sync application commands"""
		await self.wait_until_ready()
		
		await self.tree.sync()
		
	async def setup_hook(self):
		"""Initialize the bot, database, prefixes & cogs."""

		# Retrieve the bot's application info
		self.info = await self.application_info()

		# Database initialization
		server = self.config["database"]["server"]
		self.database = DataSQL(server["host"], server["port"], self.loop)
		await self.database.auth(server["user"], server["password"], server["database"])

		# Prefix per guild initialization
		self.prefixes = dict()
		for data in await self.database.select(self.config["bot"]["prefix_table"]["table"], "*"): 
			self.prefixes[data[0]] = data[1]

		# Cogs loader
		cogs = [f"cogs.{filename[:-3]}" for filename in listdir(cogs_directory) if filename.endswith(".py")]
		await cogs_manager(self, "load", cogs)

		# Sync application commands
		self.loop.create_task(self.startup())

if __name__ == '__main__':
	clean_close() # Avoid Windows EventLoopPolicy Error

	bot = Bot()
	bot.config = load_config()
	bot.logger, streamHandler = set_logging(file_level=logging.DEBUG, console_level=logging.INFO, filename="discord.log")
	bot.run(
		bot.config["bot"]["token"],
		reconnect=True,
		log_handler=streamHandler,
		log_level=logging.DEBUG, # Must be set to DEBUG, change the log_level of each handler in set_logging() method
	)