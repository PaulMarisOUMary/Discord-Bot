import discord

from discord.ext import commands
from discord.ext.commands import errors

class Errors(commands.Cog, name="errors", command_attrs=dict(hidden=True)):
	"""Errors handler"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener('on_command_error')
	async def get_command_error(self, ctx, error):
		try:
			message = await ctx.send("🕳️ There is an error.")
			if isinstance(error, commands.errors.CommandNotFound):
				await message.edit("🕳️ Command `"+str(error).split(' ')[1]+"` not found !")
			elif isinstance(error, commands.errors.NotOwner):
				await message.edit("🕳️ You must own this bot to run this command.")
			elif isinstance(error, commands.errors.CommandOnCooldown):
				await message.edit("🕳️ Command is on cooldown, wait `"+str(error).split(' ')[7]+"` !")
			elif isinstance(error, commands.errors.MissingRequiredArgument):
				command, params = ctx.command, ""
				for param in command.clean_params: params += " {"+str(param)+"}"
				await message.edit("🕳️ Something is missing. `?"+str(command)+str(params)+'`')
			elif isinstance(error, commands.errors.MemberNotFound):
				await message.edit("🕳️ Member `"+str(error).split(' ')[1]+"` not found ! Don't hesitate to ping the requested member.")
			elif isinstance(error, commands.errors.MissingPermissions):
				await message.edit("🕳️ This command require more permissions.")
			elif isinstance(error, commands.errors.DisabledCommand):
				await message.edit("🕳️ This command is disabled.")
			else:
				await message.edit("🕳️ `"+str(type(error).__name__)+"` : "+str(error))
			await ctx.message.add_reaction(emoji='❌')
		except:
			print("! Cog errors get_command_error : "+str(type(error).__name__)+" : "+str(error))

def setup(bot):
	bot.add_cog(Errors(bot))