import os
import json
import discord

from classes.database import DataSQL
from discord.ext import commands

base_directory = os.path.dirname(os.path.abspath(__file__))
bot_file = os.path.join(base_directory, "config", "bot.json")
database_file = os.path.join(base_directory, "config", "database.json")

with open(bot_file, 'r') as bdata, open(database_file, 'r') as ddata: 
	bot_data, database_data = json.load(bdata), json.load(ddata)

def get_prefix(client, message):
	guild_id, prefix = message.guild.id, None
	if guild_id in client.prefixes: prefix = client.prefixes[guild_id]
	else: prefix = bot_data["bot_default_prefix"]
	return commands.when_mentioned_or(prefix)(client, message)

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=get_prefix, description=bot_data["bot_description"], case_insensitive=True, intents=discord.Intents.all())

	async def startup(self):
		"""Sync application commands"""
		await self.wait_until_ready()
		tree = await self.tree.sync()
		print(tree)

		tree_guild = await self.tree.sync(guild=discord.Object(id=332234497078853644))
		print(tree_guild)

		print(f"Logged as: {self.user} with Discord.py{discord.__version__}")

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
		cogs_directory = os.path.join(base_directory, "cogs")
		check_counter_cogs = 0
		for filename in os.listdir(cogs_directory):
			if filename.endswith(".py"): 
				try:
					await self.load_extension(f"cogs.{filename[:-3]}")
					check_counter_cogs += 1
				except Exception as e:
					print(f"! Failed to load {filename}. | {type(e)} {e}")

		# Sync application commands & show logging informations 
		self.loop.create_task(self.startup())

if __name__ == '__main__':
	bot = Bot()
	bot.run(bot_data["token"], reconnect=True)