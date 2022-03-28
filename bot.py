import discord

from classes.database import DataSQL
from classes.utilities import cogs_manager, cogs_directory, bot_data, database_data

from os import listdir
from discord.ext import commands

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.__get_prefix, description=bot_data["bot_description"], case_insensitive=True, intents=discord.Intents.all())

	def __get_prefix(self, client, message):
		guild_id = message.guild.id
		if guild_id in client.prefixes: 
			prefix = client.prefixes[guild_id]
		else: 
			prefix = bot_data["bot_default_prefix"]
		return commands.when_mentioned_or(prefix)(client, message)

	async def on_ready(self):
		print(f"Logged as: {self.user} | discord.py{discord.__version__}\nGuilds: {len(self.guilds)} Users: {len(self.users)}")

	async def startup(self):
		"""Sync application commands"""
		await self.wait_until_ready()
		global_tree = await self.tree.sync()

		tree_guild = await self.tree.sync(guild=discord.Object(id=332234497078853644))
		print(tree_guild, global_tree)

	async def setup_hook(self):
		"""Initialize the db, prefixes & cogs."""

		#Database initialization
		self.database_data, self.bot_data, server = database_data, bot_data, database_data["server"]
		self.database = DataSQL(server["host"], server["port"])
		await self.database.auth(server["user"], server["password"], server["database"])

		# Prefix per guild initialization
		self.prefixes = dict()
		for data in await self.database.select(database_data["prefix"]["table"], "*"): 
			self.prefixes[data[0]] = data[1]

		# Cogs loader
		cogs = [f"cogs.{filename[:-3]}" for filename in listdir(cogs_directory) if filename.endswith(".py")]
		await cogs_manager(self, "load", cogs)

		# Sync application commands & show logging informations 
		self.loop.create_task(self.startup())

if __name__ == '__main__':
	bot = Bot()
	bot.run(bot_data["token"], reconnect=True)