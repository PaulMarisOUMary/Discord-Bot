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

class PrivateTextual(commands.Cog, name="privatetextual", command_attrs=dict(hidden=False)):
	"""Create and manage private textual channels"""
	def __init__(self, bot):
		self.bot = bot

	def help_custom(self):
		emoji = '💬'
		label = "Private Textual"
		description = "Add and edit textuals channels."
		return emoji, label, description

	@commands.command(name='addprivate', aliases=['create', 'add', '+', '>'], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def create_private_channel(self, ctx, *members : discord.Member):
		"""Create a private channel, use : addprivate {@USERNAME_1} {@USERNAME_2}"""
		users, mentions, down_role = [ctx.message.author], "", discord.utils.get(ctx.guild.roles, name="🎓Student")

		for g in members:
			if g.bot: raise commands.CommandError("You can't invite bots in your team.")
			else: users.append(g)
		users = list(set(users))
		if len(users) <= 1: raise commands.CommandError("You can't create a team alone.")

		role = await ctx.guild.create_role(name="team")
		team_channel = await ctx.guild.create_text_channel(name="_team_text", category=discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id))
		await team_channel.set_permissions(role, send_messages=True, view_channel=True, read_message_history=True, add_reactions=True, external_emojis=True)
		await team_channel.set_permissions(down_role, send_messages=False, view_channel=False)

		for user in users:
			await user.add_roles(role)
			mentions += " "+user.mention

		await team_channel.send(str(team_channel.mention)+" was created by "+str(ctx.message.author.mention)+".")
		await team_channel.send(mentions)
		await ctx.message.add_reaction(emoji='✅')
	
	@commands.command(name='delprivate', aliases=['delete', 'del', '-', '<'])
	async def delete_private_channel(self, ctx):
		"""Delete your private channel"""
		channel, roles = ctx.channel, get_created_roles(ctx)
		if '_' in channel.name and roles:
			await roles[0].delete()
			await channel.delete()
		else:
			raise commands.CommandError("You can't delete a non-team channel.")

	@commands.command(name='renprivate', aliases=['rename', 'ren', 'r', '_'], require_var_positional=True)
	async def rename_private_channel(self, ctx, custom_name : str):
		"""Rename your private channel, use : renprivate {NAME}"""
		channel, roles = ctx.channel, get_created_roles(ctx)
		normalize_cn, forbidden = text_to_allowed(custom_name)
		if '_' in channel.name and roles and normalize_cn:
				await channel.edit(name='_'+normalize_cn)
				await ctx.message.add_reaction(emoji='✅')
		elif not '_' in channel.name:
			raise commands.CommandError("You can't rename a non-team channel.")
		if forbidden: raise commands.CommandError("You can't use `"+str(forbidden)+"` to rename a channel.")

def setup(bot):
	bot.add_cog(PrivateTextual(bot))
