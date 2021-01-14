import time
import asyncio
import discord

from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord.utils import get
from datetime import datetime

text_channels, text_roles = [], []

async def loop_if_connected():
	GUILD, CATEGORY, MAIN_CHANNEL = "Algosup Alpha", "Voice rooms", "General"
	await bot.wait_until_ready()
	guild = discord.utils.get(bot.guilds, name=GUILD)
	category, channel = discord.utils.get(guild.categories, name=CATEGORY), discord.utils.get(guild.channels, name=MAIN_CHANNEL)
	channels = [channel]

	def channelInfos():
		empty, used = len(channels), 0
		for ch in channels:
			if ch.members:
				used += 1
		empty -= used

		return empty, used

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

async def loop_change_status():
	await bot.wait_until_ready()
	status_message, sm = ["?help","in lockdown.."], 0
	while not bot.is_closed():
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=status_message[sm], url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		if sm >= len(status_message)-1: sm = 0
		else: sm+=1

class Usefull(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(name='help', aliases=['?','h','commands'])
	async def help(self, ctx):
		embed = discord.Embed(title="Help · commands", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="**Commands **(3)\n**Remind:** Curly bracket must not be used when executing commands.", colour=0xf7346b)
		embed.set_image(url="https://cdn.discordapp.com/attachments/595057140922581003/799375656689467423/0.PNG")
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='addprivate', aliases=['+', '>'], require_var_positional=True)
	@commands.cooldown(1, 50, commands.BucketType.user)
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
	
	@commands.command(name='delprivate', aliases=['-', '<'])
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
	print("ID : "+str(bot.user.id)+"\n"+str(bot.user))

bot.add_cog(Usefull(bot))
bot.loop.create_task(loop_change_status())
bot.loop.create_task(loop_if_connected())
token_file = open("token.dat", "r").read() # path of your token file
bot.run(token_file)
