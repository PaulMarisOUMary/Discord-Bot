import time
import asyncio
import discord

from discord.ext import commands
from datetime import datetime, timedelta
from views import help as vhelp

class Basic(commands.Cog, name="basic"):
	"""Basic commands, like help, ping, ..."""
	def __init__(self, bot):
		self.bot = bot

	def help_custom(self):
		emoji = '📙'
		label = "Basic"
		description = "Basic commands, like help, ping, etc.."
		return emoji, label, description

	@commands.command(name="help", aliases=['?', 'h', "commands"])
	async def help(self, ctx, *input: str):
		"""Show the help menu."""
		if ctx.guild.id in self.bot.prefixes: guild_prefix = self.bot.prefixes[ctx.guild.id]
		else: guild_prefix = self.bot.bot_data["bot_default_prefix"]
		if not input:
			allowed = 5
			close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))
			embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Home", description = f"`Welcome to the help page.`\n\n**The prefix on this server is**: `{guild_prefix}`.\n\nUse `help command` for more info on a command.\nUse `help category` for more info on a category.\nUse the dropdown menu below to select a category.\n\u200b", url='https://github.com/PaulMarisOUMary/Algosup-Discord')
			embed.add_field(name="Time remaining :", value=f"This help session will end <t:{close_in}:R>.\nType `help` to open a new session.\n\u200b", inline=False)
			embed.add_field(name="Who am I ?", value="I'm a bot made by *WarriorMachine*. Made for Algosup in 2020.\nI have a lot of features such translator, events manager, utils, and more.\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Algosup-Discord) !")

			view = vhelp.View(bot=self.bot, ctx=ctx, homeembed=embed, ui=2)
			message = await ctx.send(embed=embed, view=view)
			try:
				await asyncio.sleep(60*allowed)
				view.stop()
				await message.delete()
				await ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")
			except: pass

		elif len(input) == 1:
			search, search_command, search_cog, embed = input[0].lower(), None, None, None
			try:
				search_command = self.bot.get_command(search)
				search_cog = self.bot.cogs[search]
			except: pass

			if search_cog:
				if "help_custom" in dir(search_cog):
					emoji, label, _ = search_cog.help_custom()
					embed = discord.Embed(title = f"{emoji} Help · {label}",description=f"`{search_cog.__doc__}`", url="https://github.com/PaulMarisOUMary/Algosup-Discord")
					for command in search_cog.get_commands():
						params = ""
						for param in command.clean_params: params += f" <{param}>"
						embed.add_field(name=f"{command.name}{params}", value=f"{command.help}\n\u200b", inline=False)
			elif search_command:
				cog = search_command.cog
				if "help_custom" in dir(cog):
					emoji, label, _ = cog.help_custom()
					embed = discord.Embed(title = f"{emoji} Help · {label} : {search_command.name}", description=f"**Command** : {search_command.name}\n{search_command.help}", url="https://github.com/PaulMarisOUMary/Algosup-Discord")
				params = ""
				for param in search_command.clean_params: params += f" <{param}>"
				embed.add_field(name="Usage", value=f"{search_command.name}{params}", inline=False)
				embed.add_field(name="Aliases", value=f"{search_command.aliases}`")
			else:
				raise commands.CommandError("Nothing found.")
			
			embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=ctx.message.author.display_avatar.url)
			await ctx.send(embed=embed)

		elif len(input) > 1:
			raise commands.CommandError("Too many arguments.")

	@commands.command(name="ping")
	async def ping(self, ctx):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.message.reply(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

def setup(bot):
	bot.add_cog(Basic(bot))
