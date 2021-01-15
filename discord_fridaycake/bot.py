import time
import asyncio
import discord

from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord.utils import get
from datetime import datetime

def get_created_roles(cont):
	wrong_roles = []
	for role in cont.guild.roles:
		perm = cont.channel.overwrites_for(role)
		if perm.send_messages:
			wrong_roles.append(role)

	return wrong_roles

async def loop_if_connected():
	GUILD, MAIN_CHANNEL = "Serveur de test", "General"
	await bot.wait_until_ready()
	guild = discord.utils.get(bot.guilds, name=GUILD)
	channel = discord.utils.get(guild.channels, name=MAIN_CHANNEL)
	category = discord.utils.get(guild.categories, id=channel.category_id)
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
	status_message, reset = ["?help","in lockdown..", "new ?+"], 0
	while not bot.is_closed():
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=status_message[reset], url='https://www.twitch.tv/warriormachine_'), status=discord.Status.dnd, afk=False)
		await asyncio.sleep(10)
		if reset >= len(status_message)-1: reset = 0
		else: reset += 1

class Usefull(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(name='help', aliases=['?','h','commands'])
	async def help(self, ctx):
		embed = discord.Embed(title="Help · commands", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="**Commands **(3)\n**Remind:** Curly bracket must not be used when executing commands.", colour=0xf7346b)
		embed.set_image(url="https://cdn.discordapp.com/attachments/595057140922581003/799375656689467423/0.PNG")
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" à "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='addprivate', aliases=['create', 'add', '+', '>'], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def create_private_channel(self, ctx, *guys : discord.Member):
		users, mentions, down_role = [ctx.message.author], "", discord.utils.get(ctx.guild.roles, name="🎓Élève")

		for g in guys:
			if g.bot: raise commands.CommandError("bot.notAllowed")
			else: users.append(g)
		users = list(set(users))
		if len(users) <= 1: raise commands.CommandError("author.isAlone")

		role = await ctx.guild.create_role(name="team")
		team_channel = await ctx.guild.create_text_channel(name="_team_text", category=discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id), sync_permissions=False)
		await team_channel.set_permissions(role, send_messages=True, view_channel=True)
		await team_channel.set_permissions(down_role, send_messages=False, view_channel=False)

		for user in users:
			await user.add_roles(role)
			mentions += " "+user.mention

		await team_channel.send(str(team_channel.mention)+" was created by "+str(ctx.message.author.mention)+".")
		await team_channel.send(mentions)
		await ctx.message.add_reaction(emoji='✅')
	
	@commands.command(name='delprivate', aliases=['delete', 'del', '-', '<'])
	async def delete_private_channel(self, ctx):
		channel, roles = ctx.channel, get_created_roles(ctx)
		if '_' in channel.name and roles:
			await roles[0].delete()
			await channel.delete()
		else:
			await ctx.send("Error, you can't delete a non-team channel.")
			await ctx.message.add_reaction(emoji='❌')

	@commands.command(name='renprivate', aliases=['rename', 'ren', 'r', '_'], require_var_positional=True)
	async def rename_private_channel(self, ctx, custom_name : str):
		channel, roles = ctx.channel, get_created_roles(ctx)
		if '_' in channel.name and roles and custom_name:
			await channel.edit(name='_'+custom_name)
			await ctx.message.add_reaction(emoji='✅')
		else:
			await ctx.send("Error, you can't rename a non-team channel.")
			await ctx.message.add_reaction(emoji='❌')

	### ERRORS ###
	@create_private_channel.error
	async def private_channel_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send('Please specify users which you want to add : `?pv @user1 @user2`')
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send('Command is on cooldown, wait `'+str(error)[-6:-4]+'s` !')
		elif str(error) == 'bot.notAllowed':
			await ctx.send("Error, you can't invite bots in your team !")
		elif str(error) == 'author.isAlone':
			await ctx.send("Error, you can't create a team alone.")
		else:
			await ctx.send('Error, check the arguments provided')
		await ctx.message.add_reaction(emoji='❌')

	@rename_private_channel.error
	async def rename_channel_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send('Please specify the custom title for the channel : `?_ {name_whitout_space}`')
		else:
			await ctx.send('Error, check the arguments provided')
		await ctx.message.add_reaction(emoji='❌')

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
