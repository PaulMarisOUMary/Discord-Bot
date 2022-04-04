import random
import discord
import asyncio

from views import fridaycake

from datetime import date, timedelta, datetime
from discord.ext import commands
from copy import deepcopy

holidays = [(date(2022, 2, 12), date(2022, 2, 19)), (date(2022, 4, 10), date(2022, 4, 23))] #Saturday -> Saturday
start = date(2022, 2, 4)#date(2021, 10, 8)#date(2021, 2, 7) #year #month #day (first friday)

def isDateInHole(date : datetime, holes : list) -> bool:
    for hole in holes:
        if date > hole[0] and date < hole[1]:
            return True
    return False

def get_dates(startthe:date, holes:list, count:int) -> list:
    fridays = []
    value = startthe
    while len(fridays) < count:
        if isDateInHole(value, holes) == False:
            fridays.append(value)
            value += timedelta(days=7)
        else:
            value += timedelta(days=7)
    return fridays

def mix_participants(participants : list, seed : int, n_group : int) -> list[list]:
	random.seed(seed)
	mixed, cache, temp = [], deepcopy(participants), []
	for _ in participants:
		n = random.randint(0, len(cache)-1)
		temp.append(cache[n])
		if len(temp) == n_group:
			mixed.append(temp)
			temp = []
		del cache[n]
	if len(temp) > 0: mixed.append(temp)
	return mixed

class FridayCake(commands.Cog, name="fridaycake", command_attrs=dict(hidden=False)):
	"""FridayCake's event commands."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.cakes = ['🎂', '🥮', '🥧', '🥯', '🧁', '🫓', '🧇', '🍞', '🍮', '🍰', '🥐']

		self.fridaycake_data = self.bot.config["database"]["fridaycake"]
		self.seed = self.fridaycake_data["seed"]

		self.bot.loop.create_task(self.initFridaycake())

	async def initFridaycake(self) -> None:
		participants = await self.bot.database.select(self.fridaycake_data["table"], "user_id, user_name", "user_isin = 1", "user_name ASC")
		participants = [[*row] for row in participants] #convert tuple of tuples to list of lists
		self.participants = mix_participants(participants, self.seed, 2)
		self.nparticipants = len(participants) #mandatory in fridaycake view

	def help_custom(self) -> tuple[str]:
		emoji = random.choice(self.cakes)
		label = "FridayCake"
		description = "Commands relative to the FridayCake event !"
		return emoji, label, description

	def all(self, ctx) -> discord.Embed:
		author = ctx.message.author
		embed = discord.Embed(title=f"{random.choice(self.cakes)} Fridaycake · All", description="`Show your personnal order of passage.`\n\u200b" ,colour=0xf7346b, url='https://github.com/PaulMarisOUMary/Algosup-Discord')
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
			
		for participants, _date in zip(self.participants, get_dates(start, holidays, len(self.participants))): 
			string = "`"
			for _id, names in participants:
				string += f"{names}` & `" if not int(_id) == author.id else f"{names}` [ᐊ](https://github.com/PaulMarisOUMary/Algosup-Discord) & `"
			embed.add_field(name=f"Friday {_date.strftime('%d %B, %Y')}", value=f"~~{string[0:-4]}~~" if date.today() >= _date else f"{string[0:-4]}", inline=False)
		return embed

	def next(self, ctx) -> discord.Embed:
		author, pin = ctx.message.author, []
		for participants, _date in zip(self.participants, get_dates(start, holidays, len(self.participants))):
			if date.today() <= _date:
				pin = (participants, _date)
				break
		if not pin:
			raise commands.CommandError("I didn't find the next participants for the Fridaycake.")
		else:
			participants = ''
			for _id, names in pin[0]:
				participants += f"<@{_id}> `{names}`\n" if not _id == author.id else f"<@{_id}> `{names}` [ᐊ](https://github.com/PaulMarisOUMary/Algosup-Discord)\n"
			embed = discord.Embed(title=f"{random.choice(self.cakes)} Fridaycake · Next", description="`Show who are the next to make a cake.`\n\u200b" ,colour=0xf7346b, url='https://github.com/PaulMarisOUMary/Algosup-Discord')
			embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
			embed.add_field(name=f"📅 Date :", value=f"Friday {pin[1].strftime('%d %B, %Y')}\n\u200b", inline=False)
			embed.add_field(name="👥 Participants :", value=participants, inline=False)
			return embed

	def when(self, author) -> discord.Embed:
		pin = None
		for participants, _date in zip(self.participants, get_dates(start, holidays, len(self.participants))): 
			for participant in participants: 
				if int(participant[0]) == author.id: 
					pin = (participants, _date)
		if not pin:
			raise commands.CommandError("You are not registered for the FridayCake.")
		else:
			participants = ''
			for _id, names in pin[0]:
				participants += f"<@{_id}> `{names}`\n" if not int(_id) == author.id else f"<@{_id}> `{names}` [ᐊ](https://github.com/PaulMarisOUMary/Algosup-Discord)\n"
			embed = discord.Embed(title=f"{random.choice(self.cakes)} Fridaycake · When", description="`Show your personnal order of passage.`\n\u200b" ,colour=0xf7346b, url='https://github.com/PaulMarisOUMary/Algosup-Discord')
			embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
			embed.add_field(name=f"👨‍🍳 Be ready for the Friday {pin[1].strftime('%d %B, %Y')} !", value=f"{author.mention}\n\u200b", inline=False)
			embed.add_field(name=f"📅 Date :", value=f"Friday {pin[1].strftime('%d %B, %Y')}\n\u200b" if date.today() <= pin[1] else f"~~Friday {pin[1].strftime('%d %B, %Y')}~~\n\u200b", inline=False)
			embed.add_field(name="👥 Participants :", value=participants, inline=False)
			return embed

	@commands.command(name='fridaycake', aliases=['f', 'fh', 'fc'])
	@commands.bot_has_permissions(send_messages=True)
	async def fridaycake(self, ctx):
		"""Show the main menu about the FridayCake event."""
		allowed = 5
		close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))

		options = [
			{'label':"Home", 'description':"Show the home page.", 'emoji':f"{self.cakes[0]}"},
			{'label':"All", 'description':"Show each participants and their dates of passage.", 'emoji':f"{self.cakes[1]}"},
			{'label':"Next", 'description':"Show the next group to pass.", 'emoji':f"{self.cakes[2]}"},
			{'label':"When", 'description':"Show your personnal order of passage.", 'emoji':f"{self.cakes[3]}"},
			{'label':"Can I trust the order of the participant list ?", 'description':"The main concept of the algorithm explained.", 'emoji':'⚙️'}
		]
		embed = discord.Embed(color=0xf7346b, title = f"{random.choice(self.cakes)} Fridaycake · Home", description = "`Welcome to the main menu about the Fridaycake.`\n\u200b", url='https://github.com/PaulMarisOUMary/Algosup-Discord')
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
		embed.add_field(name="Time remaining :", value=f"This help session will end <t:{close_in}:R>.\nType `fridaycake` to open a new session.\n\u200b", inline=False)
		embed.add_field(name="How to use this menu ?", value=f"Use the dropmenu below to select the action.", inline=False)
		
		view = fridaycake.View(options=options, placeholder="Select an action..", min_val=1, max_val=1, source=ctx, main=self, embed=embed)

		message = await ctx.send(embed=embed, view=view)
		try:
			await asyncio.sleep(60*allowed)
			view.stop()
			await message.delete()
			await ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")
		except: 
			pass

	@commands.command(name='next', aliases=['n', 'fn'])
	@commands.bot_has_permissions(send_messages=True)
	async def next_cake(self, ctx):
		"""Show who are the next to make a cake for the FridayCake event."""
		embed = self.next(ctx)
		await ctx.send(embed=embed)

	@commands.command(name='when', aliases=['w', 'fw'])
	@commands.bot_has_permissions(send_messages=True)
	async def when_cake(self, ctx, member : discord.Member = None):
		"""Show your personnal order of passage about the Fridaycake event."""
		author = ctx.message.author if not member else member
		embed = self.when(author)
		await ctx.send(embed=embed)

	@commands.command(name='all', aliases=['a', 'fa'])
	@commands.bot_has_permissions(send_messages=True)
	async def all_cake(self, ctx):
		"""Show the complete list by order for the FridayCake event."""
		embed = self.all(ctx)
		await ctx.send(embed=embed)



async def setup(bot):
	await bot.add_cog(FridayCake(bot))
