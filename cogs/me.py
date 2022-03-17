import discord

from discord.ext import commands

class Me(commands.Cog, name="me"):
	"""FridayCake's event commands."""
	def __init__(self, bot):
		self.bot = bot

		self.me_data = self.bot.database_data["me"]
		self.max_lenght_me = self.me_data["max_length"]

	def help_custom(self):
		emoji = '🤸'
		label = "Me"
		description = "Set and show a brief description of yourself."
		return emoji, label, description

	@commands.command(name="me", aliases=["description"], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def me(self, ctx, *args: str):
		"""Allows you to set or show a brief description of yourself."""
		if len(args):
			try:
				text = " ".join(args).replace("'", "''")
				if len(text) > self.max_lenght_me: raise commands.CommandError(f"The max-lenght of your *me* is set to: __{self.max_lenght_me}__ (yours is {len(text)}).")
				# Insert
				await self.bot.database.insert(self.me_data["table"], {"user_id": ctx.author.id, "user_me": text})
				# Update
				await self.bot.database.update(self.me_data["table"], "user_me", text, f"user_id = {ctx.author.id}")
				await self.show_me_message(ctx, ctx.author)
			except Exception as e:
				raise commands.CommandError(str(e))
		else:
			await self.show_me_message(ctx, ctx.author)

	@commands.command(name="sme", aliases=["showdescription", "showme"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def show_me(self, ctx, user: discord.Member = None):
		"""Allows you to show the description of other users."""
		if not user: user = ctx.author
		await self.show_me_message(ctx, user)

	async def show_me_message(self, ctx, user: discord.Member) -> None:
		response = await self.bot.database.lookup(self.me_data["table"], "user_me", "user_id", str(user.id))
		message = " ".join(response[0]) if len(response) else "No description provided.."
		await ctx.send(f"• **{user.display_name}** {message}")



def setup(bot):
	bot.add_cog(Me(bot))
