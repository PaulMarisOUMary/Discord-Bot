from discord.ext import commands

class Usefull(commands.Cog, name="usefull"):
	"""Usefull commands for Devs & more."""
	def __init__(self, bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str]:
		emoji = '🚩'
		label = "Usefull"
		description = "Usefull commands."
		return emoji, label, description

	@commands.command(name="strawpoll", aliases=["straw", "stp", "sond", "sondage"], require_var_positional=True)
	@commands.guild_only()
	async def strawpool(self, ctx, *, context):
		"""Ask a sondage, and add 2 reactions to vote with your community."""
		crossmark, checkmark = self.bot.get_emoji(842800737221607474), self.bot.get_emoji(842800730049871892)
		await ctx.message.delete()
		message = await ctx.send(f"__*{ctx.message.author.mention}*__ : {context}")
		await message.add_reaction(emoji=checkmark)
		await message.add_reaction(emoji=crossmark)



async def setup(bot):
	await bot.add_cog(Usefull(bot))
