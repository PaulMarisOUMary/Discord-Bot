import time
import discord

from discord.ext import commands


class Usefull(commands.Cog, name="usefull"):
	"""Usefull description"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='strawpoll', aliases=['straw', 'stp', 'sond', 'sondage'], pass_context=True)
	async def ping(self, ctx, *, context):
		crossmark, checkmark = self.bot.get_emoji(842800737221607474), self.bot.get_emoji(842800730049871892)
		await ctx.message.delete()
		message = await ctx.send("__*" + ctx.message.author.mention + "*__ : " + context)
		await message.add_reaction(emoji=checkmark)
		await message.add_reaction(emoji=crossmark)


	@commands.command(name='emojilist', aliases=['ce', 'el'], pass_context=True)
	async def getcustomemojis(self, ctx):
		embed_list, embed = [], discord.Embed(title="Custom Emojis List ("+str(len(ctx.guild.emojis))+") :")
		for i, emoji in enumerate(ctx.guild.emojis, start=1):
			if i == 0 : i += 1
			value = "`<:"+str(emoji.name)+":"+str(emoji.id)+">`" if not emoji.animated else "`<a:"+str(emoji.name)+":"+str(emoji.id)+">`"
			embed.add_field(name=str(self.bot.get_emoji(emoji.id))+" - **:"+str(emoji.name)+":** - (*"+str(i)+"*)",value=value)
			if i%6.25 == 400%6.25 and i != 0:
				embed_list.append(embed)
				embed = discord.Embed()
		embed_list.append(embed)

		for message in embed_list:
			await ctx.send(embed=message)

def setup(bot):
	bot.add_cog(Usefull(bot))
