import time
import asyncio
import discord

from discord.ext import commands
from datetime import datetime, timedelta
from views import help as vhelp

class Basic(commands.Cog, name="basic", command_attrs=dict(hidden=False)):
	"""Basic commands, like help, ping, ..."""
	def __init__(self, bot):
		self.bot = bot

	def help_custom(self):
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like help, ping, etc.."
		return emoji, label, description

	@commands.command(name='help', aliases=['?', 'h', 'commands'])
	async def help(self, ctx, *input):
		"""Show help command, use : help {COMMAND/CATEGORY}"""
		embed = discord.Embed(url='https://github.com/PaulMarisOUMary/Algosup-Discord')
		remind = "\n**Remind** : Hooks such as {} must not be used when executing commands."
		title, description, color = "Help · ", "", discord.Color.blue()
		if not input:
			allowed = 5
			close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))
			embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Home", description = "Welcome to the help page.\n\nUse `help command` for more info on a command.\nUse `help category` for more info on a category.\nUse the dropdown menu below to select a category.\n\u200b", url='https://github.com/PaulMarisOUMary/Algosup-Discord')
			embed.add_field(name="Time remaining :", value="This help session will end <t:"+str(close_in)+":R>.\nType `help` to open a new session.\n\u200b", inline=False)
			embed.add_field(name="Who am I ?", value="I'm a bot made by *WarriorMachine*. Made for Algosup in 2020.\nI have a lot of features such translator, events manager, utils, and more.\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Algosup-Discord) !")

			view = vhelp.View(bot=self.bot, ctx=ctx, homeembed=embed)
			message = await ctx.send(embed=embed, view=view)
			try:
				await asyncio.sleep(60*allowed)
				view.stop()
				await message.delete()
				await ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")
			except: pass
			return #end function

		elif len(input) == 1:
			search, search_command, search_cog = input[0].lower(), False, False
			try:
				search_command = self.bot.get_command(search)
				search_cog = self.bot.cogs[search]
			except: pass

			title = "Help · " + str(search)
			if search_cog:
				description, command_list = str(search_cog.__doc__), ''
				for command in search_cog.get_commands():
					command_list += "__"+str(command.name)+"__\n"+str(command.help)+'\n'
				embed.add_field(name="Commands :", value=command_list, inline=False)
			elif search_command:
				description, color = '', discord.Color.green()
				embed.add_field(name=str(search_command.name), value="__Aliases__ : `"+"`, `".join(search_command.aliases)+"`\n__Help__ : "+str(search_command.help), inline=False)
			else:
				title, description, color = "Help · Error", "Nothing was found", discord.Color.orange()

		elif len(input) > 1:
			title, description, color = "Help · Error", "Too many arguments", discord.Color.orange()

		embed.title, embed.description, embed.color = title, remind + description, color
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.display_avatar.url)
		await ctx.send(embed=embed)

	@commands.command(name='ping', pass_context=True)
	async def ping(self, ctx):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.message.reply(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

def setup(bot):
	bot.add_cog(Basic(bot))
