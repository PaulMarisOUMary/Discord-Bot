import random
import asyncio
import discord

from datetime import datetime, date
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from discord.utils import format_dt
from typing import Optional, Union

from classes.discordbot import DiscordBot
from classes.utilities import bot_has_permissions

@app_commands.guild_only()
class Birthday(commands.GroupCog, name="birthday", group_name="birthday", group_description="Commands related to birthday."):
	"""
		Set your birthday, and when the time comes I will wish you a happy birthday !
		
		Require intents: 
			- default
		
		Require bot permission:
			- view_channel
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '🎁'
		label = "Birthday"
		description = "Maybe I'll wish you soon a happy birthday !"
		return emoji, label, description

	async def cog_load(self) -> None:
		self.daily_birthday.start()

	async def cog_unload(self) -> None:
		self.daily_birthday.cancel()

	@tasks.loop(hours=1)
	async def daily_birthday(self) -> None:
		if not datetime.now().hour == 9:
			return

		await self.trigger_global_birthday()

	async def trigger_global_birthday(self, specify_guild: Optional[int] = None):
		response: tuple[tuple[int, date]] = await self.bot.database.select(self.subconfig_data["table"], "*", condition="DAY(`user_birth`) = DAY(CURRENT_DATE()) AND MONTH(`user_birth`) = MONTH(CURRENT_DATE())")
		if not response:
			self.bot.log(message = "No birthday today", name = "discord.cogs.birthday.daily_birthday")
			return

		response_guilds: list[int] = [guild for guild, _, _ in response]

		for guild in self.bot.guilds:
			if not guild.id in response_guilds:
				continue
			if specify_guild and guild.id != specify_guild:
				continue
			for channel in guild.text_channels:
				if channel.type == discord.ChannelType.forum:
					continue
				if not channel.permissions_for(guild.me).send_messages or not channel.permissions_for(guild.me).embed_links:
					continue
				if "birthday" in channel.name:
					images = [
							"https://sayingimages.com/wp-content/uploads/funny-birthday-and-believe-me-memes.jpg",
							"https://i.kym-cdn.com/photos/images/newsfeed/001/988/649/1e8.jpg",
							"https://winkgo.com/wp-content/uploads/2018/08/101-Best-Happy-Birthday-Memes-01-720x720.jpg",
							"https://www.the-best-wishes.com/wp-content/uploads/2022/01/success-kid-cute-birthday-meme-for-her.jpg"
					]
					embed = discord.Embed(
							title = "🎉 Happy birthday !",
							description = f"Today is the birthday of {'& '.join([f'<@{user_id}>' for response_guild, user_id, _ in response if guild.id == response_guild])} !",
							colour=discord.Colour.dark_gold(),
					)
					embed.set_image(url = random.choice(images))

					await channel.send(embed = embed)


	@daily_birthday.before_loop
	async def before_daily_birthday(self) -> None:
		await self.bot.wait_until_ready()
		while self.bot.database.pool is None: await asyncio.sleep(0.01) #wait_for initBirthday

	@app_commands.guild_only()
	@app_commands.command(name="set", description="Set your own birthday.")
	@app_commands.describe(month="Your month of birth.", day="Your day of birth.", year="Your year of birth.")
	@app_commands.choices(month=[Choice(name=datetime(1, i, 1).strftime("%B"), value=i) for i in range(1, 13)])
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
	async def set_birthday(self, interaction: discord.Interaction, month: int, day: app_commands.Range[int, 1, 31], year: app_commands.Range[int, datetime.now().year - 99, datetime.now().year - 15]) -> None:
		"""Allows you to set/show your birthday."""
		if day > 31 or day < 0 or year > datetime.now().year - 15 or year < datetime.now().year - 99 or not interaction.guild:
			raise ValueError("Please provide a real date of birth.")

		try:
			dataDate = datetime.strptime(f"{day}{month}{year}", "%d%m%Y").date()
			if dataDate.year > datetime.now().year - 15 or dataDate.year < datetime.now().year - 99: 
				raise commands.CommandError("Please provide your real year of birth.")
			
			await self.bot.database.insert_onduplicate(self.subconfig_data["table"], {"guild_id": interaction.guild.id, "user_id": interaction.user.id, "user_birth": dataDate})

			await self.show_birthday_message(interaction, interaction.user)
		except Exception as e:
			raise commands.CommandError(str(e))

	@app_commands.guild_only()
	@app_commands.command(name="show", description="Display the birthday of a user.")
	@app_commands.describe(user="The user to get the birthdate from.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def show_birthday(self, interaction: discord.Interaction, user: Optional[Union[discord.Member, discord.User]]) -> None:
		"""Allows you to show the birthday of other users."""
		if not user: 
			user = interaction.user
		await self.show_birthday_message(interaction, user)

	async def show_birthday_message(self, interaction: discord.Interaction, user: Union[discord.Member, discord.User]) -> None:
		response = await self.bot.database.lookup(self.subconfig_data["table"], "user_birth", {"guild_id": str(interaction.guild.id), "user_id": str(user.id)}) # type: ignore
		if response:
			birthdate : date = datetime.combine(response[0][0], datetime.min.time())
			await interaction.response.send_message(f":birthday: Birthday the {format_dt(birthdate, 'D')} and was born {format_dt(birthdate, 'R')}.")
		else:
			await interaction.response.send_message(":birthday: Nothing was found. Set the birthday and retry.")

	@bot_has_permissions(view_channel=True)
	@commands.command(name="triggerbirthday")
	@commands.is_owner()
	@commands.guild_only()
	async def trigger_birthday(self, ctx: commands.Context, guild_id: Optional[int] = None) -> None:
		"""Trigger manually the birthday."""
		if guild_id and not guild_id in [guild.id for guild in self.bot.guilds]:
			await ctx.send(f"Invalid Guild id `{guild_id}`.")
			return

		await self.trigger_global_birthday(guild_id)
		await ctx.send(f"Manually trigger birthday for `{guild_id if guild_id else 'all guilds'}`.")




async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Birthday(bot))
