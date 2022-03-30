import discord

from discord.ext import commands

def text_to_allowed(input) -> tuple[str, list]:
	out, forbidden, line = "", [], input.lower()
	for char in line:
		if not char in "abcdefghijklmnopqrstuvwxyz-_0123456789":
			forbidden.append(char)
			char = char.replace(char, '')
		out += char

	return out, forbidden

def get_created_roles(cont) -> list:
	wrong_roles = []
	for role in cont.guild.roles:
		perm = cont.channel.overwrites_for(role)
		if perm.send_messages:
			wrong_roles.append(role)

	return wrong_roles

class PrivateTextual(commands.Cog, name="privatetextual"):
	"""Create and manage private textual channels."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str]:
		emoji = '💬'
		label = "Private Textual"
		description = "Add and edit textuals channels."
		return emoji, label, description

	@commands.command(name="createprivate", aliases=["create", '+'], require_var_positional=True)
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	async def create_private_channel(self, ctx, *members : discord.Member):
		"""Create a private textual channel."""
		users, mentions, down_role = [ctx.message.author], "", discord.utils.get(ctx.guild.roles, name="🎓Student")

		for g in members:
			if g.bot: 
				raise commands.CommandError("You can't invite bots in your team.")
			else: 
				users.append(g)
		users = list(set(users))
		if len(users) <= 1: 
			raise commands.CommandError("You can't create a team alone.")

		role = await ctx.guild.create_role(name="team")
		team_channel = await ctx.guild.create_text_channel(name="_team_text", category=discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id))
		await team_channel.set_permissions(role, add_reactions=True, attach_files=True, embed_links=True, external_emojis=True, manage_messages=True, read_message_history=True, read_messages=True, send_messages=True, use_external_emojis=True, use_slash_commands=True, view_channel=True)
		try: 
			await team_channel.set_permissions(down_role, send_messages=False, view_channel=False)
		except: 
			pass

		for user in users:
			await user.add_roles(role)
			mentions += " "+user.mention

		await team_channel.send(f"{team_channel.mention} was created by {ctx.message.author.mention}.")
		await team_channel.send(mentions)
		await ctx.message.add_reaction(emoji="<a:checkmark_a:842800730049871892>")
	
	@commands.command(name="deleteprivate", aliases=["delete", '-'])
	@commands.guild_only()
	async def delete_private_channel(self, ctx):
		"""Delete your private textual channel."""
		channel, roles = ctx.channel, get_created_roles(ctx)
		if '_' in channel.name and roles:
			await roles[0].delete()
			await channel.delete()
		else:
			raise commands.CommandError("You can't delete a non-team channel.")

	@commands.command(name="renameprivate", aliases=["rename", '_'], require_var_positional=True)
	@commands.guild_only()
	async def rename_private_channel(self, ctx, custom_name : str):
		"""Rename your private textual channel."""
		channel, roles = ctx.channel, get_created_roles(ctx)
		normalize_cn, forbidden = text_to_allowed(custom_name)
		if '_' in channel.name and roles and len(normalize_cn) > 0:
			await channel.edit(name='_'+normalize_cn)
			await ctx.message.add_reaction(emoji="<a:checkmark_a:842800730049871892>")
		elif not '_' in channel.name:
			raise commands.CommandError("You can't rename a non-team channel.")
		if forbidden: 
			raise commands.CommandError(f"You can't use `{forbidden}` to rename a channel.")

	@commands.command(name="addprivate", aliases=["add", '>'], require_var_positional=True)
	@commands.guild_only()
	async def addd_to_private_channel(self, ctx, *members : discord.Member):
		"""Join a specified member to your team channel."""
		roles = get_created_roles(ctx)
		for member in members:
			if not member.bot : 
				await member.add_roles(roles[0])
			else : 
				raise commands.CommandError("You can't invite bots in your team.")
		await ctx.message.add_reaction(emoji="<a:checkmark_a:842800730049871892>")



async def setup(bot):
	await bot.add_cog(PrivateTextual(bot))