import discord
import types
import sys
import os

from discord.ext import commands
from importlib import reload

class Admin(commands.Cog, name="admin", command_attrs=dict(hidden=True)):
	"""Admin commands, you probably don't have the permission to use them"""
	def __init__(self, bot):
		self.bot = bot

	async def reload_views(self):
		modules, infants = [], []
		for module in sys.modules.items():
			if isinstance(module[1], types.ModuleType):
				modules.append(module[1])

		for module in modules:
			try:
				if os.path.basename(os.path.dirname(module.__file__)) == "views":
					reload(module)
					infants.append(module.__name__)
			except: pass

		return infants

	async def reload_cogs(self, cogs):
		victims = []
		for cog in cogs:
			norm_cog = self.bot.get_cog(cog[5:len(cog)])
			if "return_loop_task" in dir(norm_cog): 
				norm_cog.return_loop_task().cancel()
				victims.append(cog)
			self.bot.reload_extension(cog)
		return victims

	@commands.command(name='reloadall', aliases=['rell', 'relall'])
	@commands.is_owner()
	async def reload_all(self, ctx):
		"""Reload each cogs & kill each loop_tasks"""
		try:
			victims = await self.reload_cogs(self.bot.extensions)
			infants = await self.reload_views()
		except commands.ExtensionError as e:
			await ctx.send(f'{e.__class__.__name__}: {e}')
		else:
			succes_text = '💪 All cogs reloaded ! | ☠️ __`' + str(len(victims)) + ' task(s) killed`__ : '
			for victim in victims: succes_text += "`"+str(victim).replace('cogs.', '')+"` "
			succes_text += "| 🔄 __`"+str(len(infants))+" view(s) reloaded`__ : "
			for infant in infants: succes_text += "`"+str(infant).replace('views.', '')+"` "
			await ctx.send(succes_text)

	@commands.command(name='reload', aliases=['rel'], require_var_positional=True)
	@commands.is_owner()
	async def reload_cog(self, ctx, cog):
		"""Reload a spacific cog use : reload {COG}"""
		try:
			victims = await self.reload_cogs(['cogs.'+str(cog)])
		except commands.ExtensionError as e:
			await ctx.send(f'{e.__class__.__name__}: {e}')
		else:
			await ctx.send('🤘 '+cog+' reloaded ! | ☠️ __`' + str(len(victims)) + ' task killed`__ | 🔄 __`views reloaded`__')

	@commands.command(name='reloadviews', aliases=['rmod', 'rview', 'rviews'])
	@commands.is_owner()
	async def reload_view(self, ctx):
		try:
			infants = await self.reload_views()
		except commands.ExtensionError as e:
			await ctx.send(f'{e.__class__.__name__}: {e}')
		else:
			succes_text = '👌 All views reloaded ! | 🔄 __`'+str(len(infants))+' view(s) reloaded`__ : '
			for infant in infants: succes_text += "`"+str(infant).replace('views.', '')+"` "
			await ctx.send(succes_text)

	@commands.command(name='killloop', aliases=['kill'], require_var_positional=True)
	@commands.is_owner()
	async def kill_loop(self, ctx, cog):
		"""Kill the loop_task in a specific cog, use : killloop {COG}"""
		cogs = self.bot.get_cog(cog)
		if "return_loop_task" in dir(cogs):
			cogs.return_loop_task().cancel()
			await ctx.send("Task successfully killed")
		else : await ctx.send("Task not found..")

	@commands.command(name='deletechannel', aliases=['delc'], require_var_positional=True)
	@commands.is_owner()
	async def delete_channel(self, ctx, channel_name):
		"""Delete a specific channel, use : deletechannel {CHANNEL_NAME}"""
		channel = discord.utils.get(ctx.guild.channels, name=channel_name)
		while channel:
			await channel.delete()
			channel = discord.utils.get(ctx.guild.channels, name=channel_name)
		await ctx.send("All channels named `"+str(channel_name)+"` as been succesfuly deleted")

	@reload_all.error
	async def reload_all_cogs_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			await ctx.send('Error, you are not authorized to type that !')
		else:
			await ctx.send('Error')
		await ctx.message.add_reaction(emoji='❌')

	@reload_cog.error
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
