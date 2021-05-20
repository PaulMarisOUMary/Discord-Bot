import time
import discord

from discord.ext import commands

class Basic(commands.Cog, name="basic", command_attrs=dict(hidden=False)):
	"""Basic commands, like help, ping, ..."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='help', aliases=['?', 'h', 'commands'])
	async def help(self, ctx, *input):
		"""Show help command"""
		if not input:
			embed = discord.Embed(title="Help · commands", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description= "**Remind** : Hooks such as {} must not be used when executing commands.\nType `?help {CATEGORY}`", colour=discord.Color.blue())
			category_list = ''
			for cog in self.bot.cogs:
				cog_settings = self.bot.get_cog(cog).__cog_settings__
				if len(cog_settings) == 0: category_list += "{**"+str(cog).upper()+"**}\n *"+str(self.bot.cogs[cog].__doc__)+"*\n"
				elif not cog_settings['hidden']: category_list += "{**"+str(cog).upper()+"**}\n *"+str(self.bot.cogs[cog].__doc__)+"*\n"
			embed.add_field(name="Category :", value=category_list, inline=False)

		elif len(input) == 1:
			for cog in self.bot.cogs:
				if cog.lower() == input[0].lower():
					embed = discord.Embed(title="Help · " + str(cog), url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="**Description** : "+str(self.bot.cogs[cog].__doc__)+"\n**Remind** : Hooks such as {} must not be used when executing commands.", color=discord.Color.green())
					for command in self.bot.get_cog(cog).get_commands():
						aliases = ''
						if command.aliases: aliases = "__Aliases__ : "+str(command.aliases)+"\n"
						embed.add_field(name="?"+str(command.name), value=aliases+str(command.help), inline=False)
					break

				else:
					embed = discord.Embed(title="Help · Error", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="Category was not found", color=discord.Color.orange())

		elif len(input) > 1:
			embed = discord.Embed(title="Help · Error", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="Too many arguments", color=discord.Color.orange())
		
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='ping', pass_context=True)
	async def ping(self, ctx):
		"""Show latency in seconds & milliseconds"""
		before = time.monotonic()
		message = await ctx.message.reply(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

	@commands.Cog.listener('on_command_error')
	async def get_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			await ctx.send(error)
		else : await ctx.send("`C0DE 3RR0R` : " + error)

def setup(bot):
	bot.add_cog(Basic(bot))
