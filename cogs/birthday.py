import time
import random
import asyncio
import discord

from datetime import datetime, date
from discord.ext import commands, tasks
from discord.utils import get
from discord import app_commands
from discord.app_commands import Choice

class Birthday(commands.Cog, name="birthday"):
	"""
		Set your birthday, and when the time comes I will wish you a happy birthday !
		
		Require intents: 
			- default
		
		Require bot permission:
			- None
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.birthday_data = bot.config["database"]["birthday"]

	def help_custom(self) -> tuple[str]:
		emoji = '🎁'
		label = "Birthday"
		description = "Maybe I'll wish you soon a happy birthday !"
		return emoji, label, description

	async def cog_load(self):
		self.daily_birthday.start()

	async def cog_unload(self):
		self.daily_birthday.cancel()

	@tasks.loop(hours=1)
	async def daily_birthday(self):
		if datetime.now().hour == 9:
			guild = get(self.bot.guilds, id=self.birthday_data["guild_id"])
			channel = get(guild.channels, id=self.birthday_data["channel_id"])

			response = await self.bot.database.select(self.birthday_data["table"], "*")
			for data in response:
				user_id, user_birth = data

				if user_birth.month == datetime.now().month and user_birth.day == datetime.now().day:
					timestamp = round(time.mktime(user_birth.timetuple()))

					message = f"Remember this date because it's <@{user_id}>'s birthday !\nHe was born <t:{timestamp}:R> !"
					images = [
						"https://sayingimages.com/wp-content/uploads/funny-birthday-and-believe-me-memes.jpg",
						"https://i.kym-cdn.com/photos/images/newsfeed/001/988/649/1e8.jpg",
						"https://winkgo.com/wp-content/uploads/2018/08/101-Best-Happy-Birthday-Memes-01-720x720.jpg",
						"https://www.the-best-wishes.com/wp-content/uploads/2022/01/success-kid-cute-birthday-meme-for-her.jpg"
					]

					embed = discord.Embed(title="🎉 Happy birthday !", description=message, colour=discord.Colour.dark_gold())
					embed.set_image(url=images[random.randint(0, len(images)-1)])
					await channel.send(embed=embed)

	@daily_birthday.before_loop
	async def before_daily_birthday(self):
		await self.bot.wait_until_ready()
		while self.bot.database.connector is None: await asyncio.sleep(0.01) #wait_for initBirthday

	async def year_suggest(self, _: discord.Interaction, current: str):
		years = [str(i) for i in range(datetime.now().year - 99, datetime.now().year - 15)]
		if not current: 
			out = [app_commands.Choice(name=i, value=i) for i in range(datetime.now().year - 30, datetime.now().year - 15)]
		else:
			out = [app_commands.Choice(name=year, value=int(year)) for year in years if str(current) in year]
		if len(out) > 25:
			return out[:25]
		else:
			return out

	async def day_suggest(self, _: discord.Interaction, current: str):
		days = [str(i) for i in range(1, 32)]
		if not current:
			out = [app_commands.Choice(name=i, value=i) for i in range(1, 16)]
		else:
			out = [app_commands.Choice(name=day, value=int(day)) for day in days if str(current) in day]
		if len(out) > 25:
			return out[:25]
		else:
			return out

	@app_commands.command(name="birthday", description="Set your own birthday.")
	@app_commands.describe(month="Your month of birth.", day="Your day of birth.", year="Your year of birth.")
	@app_commands.choices(month=[Choice(name=datetime(1, i, 1).strftime("%B"), value=i) for i in range(1, 13)])
	@app_commands.autocomplete(day=day_suggest, year=year_suggest)
	@app_commands.checks.has_permissions(use_slash_commands=True)
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
	async def birthday(self, interaction: discord.Interaction, month: int, day: int, year: int):
		"""Allows you to set/show your birthday."""
		if day > 31 or day < 0 or year > datetime.now().year - 15 or year < datetime.now().year - 99:
			raise ValueError("Please provide a real date of birth.")

		try:
			dataDate = datetime.strptime(f"{day}{month}{year}", "%d%m%Y").date()
			if dataDate.year > datetime.now().year - 15 or dataDate.year < datetime.now().year - 99: 
				raise commands.CommandError("Please provide your real year of birth.")
			# Insert
			await self.bot.database.insert(self.birthday_data["table"], {"user_id": interaction.user.id, "user_birth": dataDate})
			# Update
			await self.bot.database.update(self.birthday_data["table"], "user_birth", dataDate, f"user_id = {interaction.user.id}")

			await self.show_birthday_message(interaction, interaction.user)
		except Exception as e:
			raise commands.CommandError(str(e))

	@app_commands.command(name="showbirthday", description="Display the birthday of a user.")
	@app_commands.describe(user="The user to get the birthdate from.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def show_birthday(self, interaction: discord.Interaction, user: discord.Member = None):
		"""Allows you to show the birthday of other users."""
		if not user: 
			user = interaction.user
		await self.show_birthday_message(interaction, user)

	async def show_birthday_message(self, interaction: discord.Interaction, user:discord.Member) -> None:
		response = await self.bot.database.lookup(self.birthday_data["table"], "user_birth", "user_id", str(user.id))
		if response:
			dataDate : date = response[0][0]
			timestamp = round(time.mktime(dataDate.timetuple()))
			await interaction.response.send_message(f":birthday: Birthday the <t:{timestamp}:D> and was born <t:{timestamp}:R>.")
		else:
			await interaction.response.send_message(":birthday: Nothing was found. Set the birthday and retry.")



async def setup(bot):
	await bot.add_cog(Birthday(bot))
