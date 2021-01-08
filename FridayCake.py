import time
import asyncio
import discord

from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord.utils import get
from datetime import datetime

#https://discord.com/oauth2/authorize?client_id=764136604284878898&scope=bot&permissions=67422272 #add bot
#https://docs.google.com/spreadsheets/d/1QeLrjctBVl1tW7tNf_WMvE1E9jj8q-70zZER4U8DyBI/edit#gid=0 #excel

data = [datetime(2020, 10, 16), datetime(2020, 10, 23), datetime(2020, 11, 6), datetime(2020, 11, 13), datetime(2020, 11, 20), datetime(2020, 11, 27), datetime(2020, 12, 4)]
participents = ["Théo", "Jules", "Paul", "Steevy", "Salah", "Karine", "Laura-lee", "Clément", "Louis", "Florent", "Martin", "Laurent", "Aurélien", "Eric"]

def numServers():
	servers = 0
	for guild in bot.guilds:
		servers += 1
	return servers

def numMembers():
	members = 0
	for guild in bot.guilds:
		for member in guild.members:
			members += 1
	return members

def whoisnext():
	now = datetime.now()
	guys = ["Théo Jules", "Paul Steevy", "Salah Karine", "Laura-lee Clément", "Louis Florent", "Martin Laurent", "Aurélien Eric"]
	daysresult = []

	for i in data:
		difference = i-now
		if not difference.days < 0:
			daysresult.append(difference.days)
	num = len(data)-len(daysresult)
	return guys[num], data[num]

def wheniamlisted(ctx):
	name = ctx.message.author.display_name
	status = False
	for g in participents:
		if g.lower().replace('é', 'e') == name.lower().replace('é', 'e'):
			status = True
	return status

def wheniam(ctx):
	name = ctx.message.author.display_name
	data_participents = [datetime(2020, 10, 16), datetime(2020, 10, 16),
						datetime(2020, 10, 23), datetime(2020, 10, 23),
						datetime(2020, 11, 6), datetime(2020, 11, 6),
						datetime(2020, 11, 13), datetime(2020, 11, 13),
						datetime(2020, 11, 20), datetime(2020, 11, 20),
						datetime(2020, 11, 27), datetime(2020, 11, 27),
						datetime(2020, 12, 4), datetime(2020, 12, 4)]
	status = False
	counter = 0
	for g in participents:
		if g.lower().replace('é', 'e') == name.lower().replace('é', 'e'):
			status = True
		if not status:
			counter += 1

	counter = data_participents[counter]

	return name, counter
		
async def if_connected():
	await bot.wait_until_ready()
	guild = discord.utils.get(bot.guilds, name="Serveur de test")
	channel = discord.utils.get(guild.channels, name="Général")
	channels = [channel]

	while not bot.is_closed():

		is_member = 0
		for ch in channels:
			if ch.members:
				is_member += 1

		if is_member >= len(channels):
			named = "Vocal "+str(len(channels))
			exist_channel = discord.utils.get(guild.channels, name=named)
			if not exist_channel:
				category = discord.utils.get(guild.categories, name="Salons vocaux")
				a = await guild.create_voice_channel(name=named, category=category)
				channels.append(a)
			else :
				await exist_channel.delete()
		elif is_member+1 < len(channels):
			if len(channels) > 1:
				count = 1
				for ch in channels:
					if not ch.members:
						if len(channels) > 2:
							await channels[count+1].delete()
							del channels[count+1]
						else:
							await channels[count].delete()
							del channels[count]
						count += 1

		await asyncio.sleep(0.5)


async def my_background_task():
	await bot.wait_until_ready()
	while not bot.is_closed():
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="Corona is near..", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="?help", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		"""await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name='?help', url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="?next", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="?when", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="?all", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)"""

class Usefull(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(name='?', aliases=['h', 'help', 'aide'])
	async def help(self, ctx):
		embed = discord.Embed(title="Page d'aide ·", colour=0xf7346b)
		embed.set_thumbnail(url=ctx.me.avatar_url)
		embed.add_field(name="?help", value="ou ?h | ?? | ?aide \n```fix\naffiche la liste des commandes```", inline=False)
		embed.add_field(name="?next", value="ou ?n \n```fix\naffiche qui est le prochain à préparer un dessert```", inline=False)
		embed.add_field(name="?when", value="ou ?w \n```fix\naffiche quand est-ce que tu dois préparer ton dessert```", inline=False)
		embed.add_field(name="?all", value="ou ?a \n```fix\naffiche la liste complete des cuistots et de leurs date de préparation```", inline=False)
		embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='all', aliases=['a'])
	async def all(self, ctx):
		embed = discord.Embed(title="All ·", colour=0xf7346b)
		embed.set_thumbnail(url=ctx.me.avatar_url)
		embed.add_field(name="Vendredi 16 octobre", value="`Théo` `Jules`", inline=False)
		embed.add_field(name="Vendredi 23 octobre", value="`Paul` `Steevy`", inline=False)
		embed.add_field(name="Vendredi 06 novembre", value="`Salah` `Karine`", inline=False)
		embed.add_field(name="Vendredi 13 novembre", value="`Laura-lee` `Clément`", inline=False)
		embed.add_field(name="Vendredi 20 novembre", value="`Louis` `Florent`", inline=False)
		embed.add_field(name="Vendredi 27 novembre", value="`Martin` `Laurent`", inline=False)
		embed.add_field(name="Vendredi 04 décembre", value="`Aurélien` `Eric`", inline=False)
		embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='next', aliases=['n'])
	async def next(self, ctx):
		guys, date = whoisnext()
		embed = discord.Embed(title="Next ·", colour=0xf7346b)
		embed.set_thumbnail(url=ctx.me.avatar_url)
		embed.add_field(name="Les prochains cuistots sont :", value="`{}` pour le `Vendredi {}`".format(guys.replace(' ', '` et `'), date.strftime("%d %b")), inline=False)
		embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='when', aliases=['w'])
	async def when(self, ctx):
		stat = wheniamlisted(ctx)
		if stat:
			name, date = wheniam(ctx)
			embed = discord.Embed(title="When ·", colour=0xf7346b)
			embed.set_thumbnail(url=ctx.me.avatar_url)
			embed.add_field(name="{} soit prêt(e) pour le".format(name), value="`Vendredi {}`".format(date.strftime("%d %b")), inline=False)
			embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
			await ctx.send(embed=embed)
		else:
			embed = discord.Embed(title="When ·", colour=0xf7346b)
			embed.set_thumbnail(url=ctx.me.avatar_url)
			embed.add_field(name="Voyons voir..", value="je ne trouve pas ton nom sur la liste, sorry !", inline=False)
			embed.set_footer(text="Requête de : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
			await ctx.send(embed=embed)

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),description='FridayCake',case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
	print("ID : "+str(bot.user.id))
	print(str(bot.user))

bot.add_cog(Usefull(bot))
bot.loop.create_task(my_background_task())
bot.loop.create_task(if_connected())
token_file = "XXXXXXXXXXX.XXXXX.XXXXX" # replace me
bot.run(token_file)
