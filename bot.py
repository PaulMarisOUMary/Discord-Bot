import os
import discord

from discord.ext import commands

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), description='_Clan-of-Ghosts_', intents=intents)
bot.remove_command('help')

current_directory = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
	cogs_directory = os.path.join(current_directory, "cogs")
	for cog in os.listdir(cogs_directory):
		actual = os.path.splitext(cog)
		if actual[1] == '.py':
			bot.load_extension('cogs.'+actual[0])

@bot.event
async def on_ready():
	print("Logged in as: "+str(bot.user)+"\nVersion: "+str(discord.__version__))

token_file = open(os.path.join(current_directory, "auth", "token.dat"), "r").read()
bot.run(token_file, bot=True, reconnect=True)
