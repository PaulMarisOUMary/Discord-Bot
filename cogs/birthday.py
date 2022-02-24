import os
import json
import time
import random
import asyncio
import discord

from classes.database import DataSQL

from datetime import datetime, date
from discord.ext import commands, tasks

auth_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth", "auth.json")
with open(auth_directory, "r") as data: database_data = json.load(data)["database"]
birthday_data = database_data["birthday"]

class Birthday(commands.Cog, name="birthday"):
	"""I'll wish you soon a happy birthday!"""
	def __init__(self, bot):
		self.bot = bot

		self.bot.loop.create_task(self.initBirthday())
		self.daily_birthday.start()

	async def initBirthday(self):
		self.database = DataSQL(database_data["host"], database_data["port"])
		await self.database.auth(database_data["user"], database_data["password"], birthday_data["database"])

	def cog_unload(self):
		self.daily_birthday.cancel()

	@tasks.loop(hours=1)
	async def daily_birthday(self):
		if datetime.now().hour == 9:
			guild = self.bot.get_guild(int(birthday_data["guild_id"]))
			channel = guild.get_channel(int(birthday_data["channel_id"]))

			response = await self.database.select(birthday_data["table"], "*")
			for data in response:
				user_id, user_birth = data[0], data[1]

				if user_birth.month == datetime.now().month and user_birth.day == datetime.now().day:
					timestamp = round(time.mktime(user_birth.timetuple()))

					message = f"Remembed this date because it's <@{str(user_id)}>'s birthday !\nHe was born <t:{timestamp}:R> !"
					images = [
						"https://sayingimages.com/wp-content/uploads/funny-birthday-and-believe-me-memes.jpg",
						"https://i.kym-cdn.com/photos/images/newsfeed/001/988/649/1e8.jpg",
						"https://winkgo.com/wp-content/uploads/2018/08/101-Best-Happy-Birthday-Memes-01-720x720.jpg",
						"https://www.the-best-wishes.com/wp-content/uploads/2022/01/success-kid-cute-birthday-meme-for-her.jpg"]

					embed = discord.Embed(title="🎉 Happy birthday !", description=message, colour=discord.Colour.dark_gold())
					embed.set_image(url=images[random.randint(0, len(images)-1)])
					await channel.send(embed=embed)

	@daily_birthday.before_loop
	async def before_daily_birthday(self):
		await self.bot.wait_until_ready()
		while self.database.connector is None: await asyncio.sleep(0.01) #wait_for initBirthday

	@commands.command(name='birthday', aliases=['bd', 'setbirthday', 'setbirth', 'birth'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def birthday(self, ctx, date: str = None):
		"""Allows you to set/show your birthday."""
		if date:
			try:
				dataDate = datetime.strptime(date, "%d/%m/%Y").date()
				if dataDate.year > datetime.now().year - 15 or dataDate.year < datetime.now().year - 99: raise commands.CommandError("Please provide your real year of birth.")
				# Insert
				await self.database.insert(birthday_data["table"], {"user_id": ctx.author.id, "user_birth": dataDate})
				# Update
				await self.database.update(birthday_data["table"], "user_birth", dataDate, "user_id = "+str(ctx.author.id))

				await self.show_birthday_message(ctx, ctx.author)
			except ValueError:
				raise commands.CommandError("Invalid date format, try : `dd/mm/yyyy`.\nExample : `26/12/1995`")
			except Exception as e:
				raise commands.CommandError(str(e))
		else:
			await self.show_birthday(ctx, ctx.author)

	@commands.command(name='showbirthday', aliases=['showbirth', 'sbd'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def show_birthday(self, ctx, user:discord.Member = None):
		"""Allows you to show the birthday of other users."""
		if not user: user = ctx.author
		await self.show_birthday_message(ctx, user)

	async def show_birthday_message(self, ctx, user:discord.Member) -> None:
		response = await self.database.lookup(birthday_data["table"], "user_birth", "user_id", str(user.id))
		if response:
			dataDate : date = response[0][0]
			timestamp = round(time.mktime(dataDate.timetuple()))
			await ctx.send(f":birthday: Birthday the <t:{timestamp}:D> and was born <t:{timestamp}:R>.")
		else:
			await ctx.send(":birthday: Nothing was found. Set the birthday and retry.")



def setup(bot):
	bot.add_cog(Birthday(bot))
