import discord

from discord.ext import commands

def text_to_allowed(input):
	out, forbidden, line = "", [], input.lower()
	for char in line:
		if not char in "abcdefghijklmnopqrstuvwxyz-éèà¤£€µù§_0123456789":
			forbidden.append(char)
			char = char.replace(char,'')
		out += char.lower()

	return out, forbidden

def get_created_roles(cont):
	wrong_roles = []
	for role in cont.guild.roles:
		perm = cont.channel.overwrites_for(role)
		if perm.send_messages:
			wrong_roles.append(role)

	return wrong_roles

class PrivateTextual(commands.Cog, name="privatetextual"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='addprivate', aliases=['create', 'add', '+', '>'], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def create_private_channel(self, ctx, *guys : discord.Member):
		users, mentions, down_role = [ctx.message.author], "", discord.utils.get(ctx.guild.roles, name="🎓Student")

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
		normalize_cn, forbidden = text_to_allowed(custom_name)
		if '_' in channel.name and roles and normalize_cn:
				await channel.edit(name='_'+normalize_cn)
				await ctx.message.add_reaction(emoji='✅')
		elif not '_' in channel.name:
			await ctx.send("Error, you can't rename a non-team channel.")
			await ctx.message.add_reaction(emoji='❌')
		if forbidden: await ctx.send(":warning: you can't use `"+str(forbidden)+"` to rename a channel.")

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

def setup(bot):
	bot.add_cog(PrivateTextual(bot))
