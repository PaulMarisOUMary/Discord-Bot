import time
import asyncio
import discord

from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord.utils import get
from datetime import datetime

#https://discord.com/oauth2/authorize?client_id=764136604284878898&scope=bot&permissions=67422272

data = [datetime(2020, 10, 16), datetime(2020, 10, 23), datetime(2020, 11, 6), datetime(2020, 11, 13), datetime(2020, 11, 20), datetime(2020, 11, 27), datetime(2020, 12, 4)]
participents = ["Théo", "Jules", "Paul", "Steevy", "Salah", "Karine", "Laura-lee", "Clément", "Louis", "Florent", "Martin", "Laurent", "Aurélien", "Eric"]
text_channels = []
text_roles = []

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
	groups = ["Théo Jules", "Paul Steevy", "Salah Karine", "Laura-lee Clément", "Louis Florent", "Martin Laurent", "Aurélien Eric"]
	daysresult = []

	for i in data:
		difference = i-now
		if not difference.days < 0:
			daysresult.append(difference.days)
	num = len(data)-len(daysresult)
	return groups[num], data[num]

def wheniamlisted(ctx):
	name = ctx.message.author.display_name
	status = False
	for g in participents:
		if g.lower().replace('é', 'e') == name.lower().replace('é', 'e'):
			status = True
	return status

def wheniam(ctx):
	name = ctx.message.author.display_name
	data_participents = []
	for c in data:
		data_participents.append(c)
		data_participents.append(c)

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
	GUILD, CATEGORY, MAIN_CHANNEL = "Serveur de test", "Voice rooms", "General"
	await bot.wait_until_ready()
	guild = discord.utils.get(bot.guilds, name=GUILD)
	category = discord.utils.get(guild.categories, name=CATEGORY)
	channel = discord.utils.get(guild.channels, name=MAIN_CHANNEL)
	channels = [channel]

	def getMissingChannel(): #old function to get which channel is missing #useless now..
		actual, missing, normal = [], [], []
		for ch in channels:
			num = ch.name.partition(' ')
			if num[-1].isdigit():
				actual.append(int(num[-1]))
		actual = sorted(actual)
		if len(actual) < 1: missing.append(1)
		else : [normal.append(x) for x in range(1, actual[-1]+1)]

		for i, no in enumerate(normal):
			if i < len(actual):
				if no != actual[i] and no not in actual:
					missing.append(no)
			elif no not in actual:
				missing.append(no)

		if len(missing) < 1: missing.append(actual[-1]+1)

		return missing[0]

	def channelInfos():
		emptyChannels, usedChannels = len(channels), 0
		for ch in channels:
			if ch.members:
				usedChannels += 1
		emptyChannels -= usedChannels

		return emptyChannels, usedChannels

	while not bot.is_closed():
		emptyChannels, usedChannels = channelInfos()
		is_change = False

		if usedChannels == len(channels):
			a = await guild.create_voice_channel(name="Vocal", category=category, sync_permissions=True)
			channels.append(a)
			is_change = True

		elif emptyChannels > 1:
			count, lock = 0, False
			for ch in channels:
				if not ch.members and not ch.name == MAIN_CHANNEL and not lock:
					await ch.delete()
					del channels[count]
					lock = True
				count += 1
			is_change = True

		if is_change:
			for i, ch in enumerate(channels):
				if not ch.name == MAIN_CHANNEL:
					await ch.edit(name="Vocal "+str(i))

		await asyncio.sleep(0.1)

async def my_background_task():
	await bot.wait_until_ready()
	while not bot.is_closed():
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="en confinement..", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="?help", url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)

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
		embed.add_field(name="?pv @user1 @user2", value="ou ?> \n```fix\ncréer un salon textuel privé```", inline=False)
		embed.add_field(name="?dpv", value="ou ?< \n```fix\nsuprime votre salon textuel privé```", inline=False)
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

	@commands.command(name='pv', aliases=['>'], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def private_channels(self, ctx, *guys : discord.Member):
		text_category, users, mentions, you_in, down_role = discord.utils.get(ctx.guild.categories, name="Text rooms"), [], "", False, discord.utils.get(ctx.guild.roles, name="🎓Élève")

		for g in guys:
			if g.bot: raise commands.CommandError("bot.notAllowed")
			else: users.append(g)
			if g.id == ctx.message.author.id: you_in = True
		if not you_in: raise commands.CommandError("author.requestedIn")
		elif len(guys) <= 1: raise commands.CommandError("author.isAlone")

		role = await ctx.guild.create_role(name="tr_"+str(len(text_roles)+1))
		a = await ctx.guild.create_text_channel(name="team_text_"+str(len(text_channels)+1), category=text_category, sync_permissions=False)
		await a.set_permissions(ctx.guild.default_role, send_messages=False, view_channel=False)
		await a.set_permissions(role, send_messages=True, view_channel=True)
		await a.set_permissions(down_role, send_messages=False, view_channel=False)
		text_channels.append(a)
		text_roles.append(role)

		for m in users:
			await m.add_roles(role)
			mentions += " "+m.mention
		
		await a.send("The text_team_"+str(len(text_channels))+" was created by "+str(ctx.message.author.mention)+".")
		await a.send(mentions)
	
	@commands.command(name='dpv', aliases=['<'])
	async def delete_private_channels(self, ctx):
		channel_name, is_error, deleted = ctx.channel.name, True, False
		for i, ch in enumerate(text_channels):
			if ch.name == channel_name:
				await ch.delete()
				del text_channels[i]
				await text_roles[i].delete()
				del text_roles[i]
				is_error, deleted = False, True

		if not deleted and channel_name[0:10] == "team_text_":
			await ctx.channel.delete()
			is_error = False
		
		if is_error:
			await ctx.send("Error, you can't delete this channel")

	### ERRORS ###
	@private_channels.error
	async def pv_command_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send('Please specify users which you want to add : `?pv @user1 @user2`')
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send('Command is on cooldown, wait `'+str(error)[-6:-4]+'s` !')
		elif str(error) == 'bot.notAllowed':
			await ctx.send("Error, you can't invite bots in your team !")
		elif str(error) == 'author.requestedIn':
			await ctx.send("Error, you are not in the group !")
		elif str(error) == 'author.isAlone':
			await ctx.send("Error, you can't create a team alone.")
		else:
			await ctx.send('Error, check the arguments provided')

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),description='FridayCake',case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
	print("ID : "+str(bot.user.id))
	print(str(bot.user))

bot.add_cog(Usefull(bot))
bot.loop.create_task(my_background_task())
bot.loop.create_task(if_connected())
token_file = open("token.dat", "r").read() # path of your token file
bot.run(token_file)
