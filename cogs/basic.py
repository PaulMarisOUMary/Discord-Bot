import time
import discord

from discord.ext import commands

class Basic(commands.Cog, name="basic"):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(name='help', aliases=['?','h','commands'])
	async def help(self, ctx):
		embed = discord.Embed(title="Help · commands", url="https://github.com/PaulMarisOUMary/Algosup-Discord", description="**Commands **(3)\n**Remind:** Curly bracket must not be used when executing commands.", colour=0xf7346b)
		embed.set_image(url="https://cdn.discordapp.com/attachments/595057140922581003/799375656689467423/0.PNG")
		embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='ping', pass_context=True)
	async def ping(self, ctx):
		before = time.monotonic()
		message = await ctx.message.reply(":ping_pong: Pong !")
		ping = (time.monotonic() - before) * 1000
		await message.edit(content=f":ping_pong: Pong ! in `{float(round(ping/1000.0,3))}s` ||{int(ping)}ms||")

	@commands.Cog.listener('on_command_error')
	async def get_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			await ctx.send(error)

def setup(bot):
	bot.add_cog(Basic(bot))
