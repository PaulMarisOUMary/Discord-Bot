import os
import discord

from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),description='FridayCake',case_insensitive=True)
bot.remove_command('help')

if __name__ == '__main__':
	if os.name == 'nt':
		end = '\\cogs'
	elif os.name == 'posix':
		end = '/cogs'
	files = os.listdir(os.getcwd()+end)
	for cog in files:
		if cog[-3:len(cog)] == '.py':
			bot.load_extension('cogs.'+cog[:-3])

@bot.event
async def on_ready():
	print("Logged in as: "+str(bot.user)+"\nVersion: "+str(discord.__version__))

token_file = open("token.dat", "r").read()
bot.run(token_file, bot=True, reconnect=True)
