import os
import json
import discord

from classes.database import DataSQL

from discord.ext import commands

auth_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth", "auth.json")
with open(auth_directory, "r") as data: database_data = json.load(data)["database"]
me_data = database_data["me"]
max_lenght_me = 255

class Me(commands.Cog, name="me", command_attrs=dict(hidden=False)):
	"""FridayCake's event commands."""
	def __init__(self, bot):
		self.bot = bot
		
		self.bot.loop.create_task(self.initMe())

	def help_custom(self):
		emoji = '🤸'
		label = "Me"
		description = "Set and show a brief description of yourself."
		return emoji, label, description

	def cog_unload(self) -> None:
		self.database.close()

	async def initMe(self):
		self.database = DataSQL(database_data["host"], database_data["port"])
		await self.database.auth(database_data["user"], database_data["password"], database_data["fridaycake"]["database"])

	@commands.command(name='me', aliases=['description'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def me(self, ctx, *args:str):
		"""Allows you to set or show a brief description of yourself."""
		if len(args):
			try:
				text = " ".join(args).replace("'", "''")
				if len(text) > max_lenght_me: raise commands.CommandError("The max-lenght of your *me* is set to: __"+str(max_lenght_me)+"__ (yours is "+str(len(text))+").")
				# Insert
				await self.database.insert(me_data["table"], {"user_id": ctx.author.id, "user_me": text})
				# Update
				await self.database.update(me_data["table"], "user_me", text, "user_id = "+str(ctx.author.id))
				await self.show_me_message(ctx, ctx.author)
			except Exception as e:
				raise commands.CommandError(str(e))
		else:
			await self.show_me_message(ctx, ctx.author)

	@commands.command(name='sme', aliases=['showdescription', 'showme'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def show_me(self, ctx, user:discord.Member = None):
		"""Allows you to show the description of other users."""
		if not user: user = ctx.author
		await self.show_me_message(ctx, user)

	async def show_me_message(self, ctx, user:discord.Member) -> None:
		response = await self.database.lookup(me_data["table"], "user_me", "user_id", str(user.id))
		message = " ".join(response[0]) if len(response) else "No description provided.."
		await ctx.send("• **"+ user.display_name + "** " + message)



def setup(bot):
	bot.add_cog(Me(bot))
