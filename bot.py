import os
import json
import discord

from classes.database import DataSQL
from discord.ext import commands

base_directory = os.path.dirname(os.path.abspath(__file__))
bot_file = os.path.join(base_directory, "config", "bot.json")
database_file = os.path.join(base_directory, "config", "database.json")

with open(bot_file, "r") as bdata, open(database_file, "r") as ddata: 
	bot_data, database_data = json.load(bdata), json.load(ddata)

def get_prefix(client, message) -> str:
	guild_id = message.guild.id
	if guild_id in client.prefixes: return client.prefixes[guild_id]
	return bot_data["bot_default_prefix"]

async def initBot() -> None:
	"""Initialize the bot."""
	# Database connector
	bot.database_data, bot.bot_data, server = database_data, bot_data, database_data["server"]
	bot.database = DataSQL(server["host"], server["port"])
	await bot.database.auth(server["user"], server["password"], server["database"])

	# Prefixes loader
	bot.prefixes = dict()
	for data in await bot.database.select(database_data["prefix"]["table"], "*"): bot.prefixes[data[0]] = data[1]

	# Cogs loader
	cogs_directory = os.path.join(base_directory, "cogs")
	for cog in os.listdir(cogs_directory):
		actual = os.path.splitext(cog)
		if actual[1] == '.py': bot.load_extension('cogs.'+actual[0])

if __name__ == '__main__':
	#If you're not using any database replace the "command_prefix" with : commands.when_mentioned_or(bot_data["bot_default_prefix"])
	bot = commands.Bot(command_prefix=get_prefix, description=bot_data["bot_description"], case_insensitive=True, intents=discord.Intents.all(), help_command=None)
	bot.loop.create_task(initBot())

	@bot.event
	async def on_ready():
		print("Logged in as: "+str(bot.user)+"\nVersion: "+str(discord.__version__))

	bot.run(bot_data["token"], reconnect=True)