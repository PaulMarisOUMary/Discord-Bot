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
	for cog in os.listdir(current_directory+"\\cogs"):
		if cog[-3:len(cog)] == '.py':
			bot.load_extension('cogs.'+cog[:-3])

@bot.event
async def on_ready():
	print("Logged in as: "+str(bot.user)+"\nVersion: "+str(discord.__version__))

token_file = open(current_directory+"\\auth\\token.dat", "r").read()
bot.run(token_file, bot=True, reconnect=True)
