from discord.ext import commands

class Errors(commands.Cog, name="errors"):
	"""Errors handler."""
	def __init__(self, bot) -> None:
		self.bot = bot

	"""def help_custom(self):
		emoji = "<a:crossmark:842800737221607474>"
		label = "Error"
		description = "A custom errors handler. Nothing to see here."
		return emoji, label, description"""

	@commands.Cog.listener("on_error")
	async def get_error(self, event, *args, **kwargs):
		"""Error handler"""
		print(f"! Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.")

	@commands.Cog.listener("on_command_error")
	async def get_command_error(self, ctx, error):
		"""Command Error handler"""
		try:
			message = await ctx.send("🕳️ There is an error.")
			if isinstance(error, commands.errors.CommandNotFound):
				await message.edit(f"🕳️ Command `{str(error).split(' ')[1]}` not found !")
			elif isinstance(error, commands.errors.NotOwner):
				await message.edit("🕳️ You must own this bot to run this command.")
			elif isinstance(error, commands.errors.NoPrivateMessage):
				await message.edit("🕳️ This command cannot be used in a private message.")
			elif isinstance(error, commands.errors.CommandOnCooldown):
				await message.edit(f"🕳️ Command is on cooldown, wait `{str(error).split(' ')[7]}` !")
			elif isinstance(error, commands.errors.MissingRequiredArgument):
				command, params = ctx.command, ""
				for param in command.clean_params: 
					params += " {"+str(param)+'}'
				await message.edit(f"🕳️ Something is missing. `?{command}{params}`")
			elif isinstance(error, commands.errors.MemberNotFound):
				await message.edit(f"🕳️ Member `{str(error).split(' ')[1]}` not found ! Don't hesitate to ping the requested member.")
			elif isinstance(error, commands.errors.MissingPermissions):
				await message.edit("🕳️ This command require more permissions.")
			elif isinstance(error, commands.errors.DisabledCommand):
				await message.edit("🕳️ This command is disabled.")
			else:
				await message.edit(f"🕳️ `{type(error).__name__}` : {error}")
			await ctx.message.add_reaction(emoji='<a:crossmark:842800737221607474>') #❌
		except Exception as e:
			print(f"! Cogs.errors get_command_error : {type(error).__name__} : {error}\n! Internal Error : {e}\n")



async def setup(bot):
	await bot.add_cog(Errors(bot))