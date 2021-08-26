import time
import discord

from discord.ext import commands

class Basic(commands.Cog, name="basic", command_attrs=dict(hidden=False)):
	"""Basic commands, like help, ping, ..."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='help', aliases=['?', 'h', 'commands'])
	async def help(self, ctx, *input):
		"""Show help command, use : help {COMMAND/CATEGORY}"""
		embed = discord.Embed(url='https://github.com/PaulMarisOUMary/Algosup-Discord')
		remind = "\n**Remind** : Hooks such as {} must not be used when executing commands."
		title, description, color = "Help · ", "", discord.Color.blue()
		if not input:
			category_list = ''
			for cog in self.bot.cogs:
				cog_settings = self.bot.get_cog(cog).__cog_settings__
				if len(cog_settings) == 0 or not cog_settings['hidden']: category_list += "{**"+str(cog).upper()+"**}\n *"+str(self.bot.cogs[cog].__doc__)+"*\n"
			embed.add_field(name="Category :", value=category_list, inline=False)

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

	@commands.Cog.listener('on_command_error')
	async def get_command_error(self, ctx, error):
		if isinstance(error, commands.errors.CommandNotFound):
			try:
				message = await ctx.send('🕳️ Command not found !')
				await message.edit("🕳️ `"+str(type(error).__name__)+"` : "+str(error))
			except: pass
		else:
			try:
				message = await ctx.send('🕳️ There is an error.')
				await message.edit("🕳️ `"+str(type(error).__name__)+"` : "+str(error))
			except: pass
		await ctx.message.add_reaction(emoji='❌')

def setup(bot):
	bot.add_cog(Basic(bot))
