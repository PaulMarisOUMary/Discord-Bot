import os
import json
import discord

from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), description='Algobot', intents=intents, help_command=None)

base_directory = os.path.dirname(os.path.abspath(__file__))
auth_file = os.path.join(base_directory, "auth", "auth.json")

with open(auth_file, "r") as data: json_data = json.load(data)

if __name__ == '__main__':
	cogs_directory = os.path.join(base_directory, "cogs")
	for cog in os.listdir(cogs_directory):
		actual = os.path.splitext(cog)
		if actual[1] == '.py':
			bot.load_extension('cogs.'+actual[0])

@bot.event
async def on_ready():
	print("Logged in as: "+str(bot.user)+"\nVersion: "+str(discord.__version__))

bot.run(json_data["token"], reconnect=True)