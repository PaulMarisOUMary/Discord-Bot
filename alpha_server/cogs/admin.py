import os
import discord

from discord.ext import commands

async def is_owner(ctx):
	return ctx.author.id == 265148938091233293

class Admin(commands.Cog, name="admin", command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='reloadall', aliases=['rell', 'relall'])
	@commands.check(is_owner)
	async def reload_all_cogs(self, ctx):
		botCogs, safeCogs = self.bot.extensions, []
		try:
			for cog in botCogs:
				safeCogs.append(cog)
			for cog in safeCogs:
				g_cog = self.bot.get_cog(cog[5:len(cog)])
				if "return_loop_task" in dir(g_cog): g_cog.return_loop_task().cancel()
				self.bot.reload_extension(cog)
		except commands.ExtensionError as e:
			await ctx.send(f'{e.__class__.__name__}: {e}')
		else:
			await ctx.send(':muscle:  All cogs reloaded !')

	@commands.command(name='reload', aliases=['rel'], require_var_positional=True)
	@commands.check(is_owner)
	async def reload_cogs(self, ctx, cog):
		cog = 'cogs.'+cog
		try:
			self.bot.reload_extension(cog)
		except commands.ExtensionError as e:
			await ctx.send(f'{e.__class__.__name__}: {e}')
		else:
			await ctx.send(':metal: '+cog+' reloaded !')

	@commands.command(name='killloop', aliases=['kill'], require_var_positional=True)
	@commands.check(is_owner)
	async def kill_loop(self, ctx, cog):
		cogs = self.bot.get_cog(cog)
		if "return_loop_task" in dir(cogs):
			cogs.return_loop_task().cancel()
		await ctx.send("Task successfully killed")

	@reload_all_cogs.error
	async def reload_cogs_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			await ctx.send('Error, you are not authorized to type that !')
		else:
			await ctx.send('Error')
		await ctx.message.add_reaction(emoji='❌')

	@reload_cogs.error
	async def reload_cogs_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send('Please specify which cogs')
		elif isinstance(error, commands.CheckFailure):
			await ctx.send('Error, you are not authorized to type that !')
		else:
			await ctx.send('Error, check the argument(s) provided')
		await ctx.message.add_reaction(emoji='❌')
	
	

def setup(bot):
	bot.add_cog(Admin(bot))
