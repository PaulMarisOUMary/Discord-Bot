import time
import random
import discord

from datetime import date, timedelta
from discord.ext import commands

groups = ["Karine Aurélien", "Eloi Louis", "Brendon Laura-Lee"] #, "Jules Martin", "Théo Paul"
start = date(2021, 2, 5)

def getFriday(date, count):
    date += timedelta(days = 4 - date.weekday())
    for i in range(count):
        yield date
        date += timedelta(days = 7)

class FridayCake(commands.Cog, name="fridaycake", command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='cake', aliases=['fc'])
	async def cake(self, ctx):
		emoji_choices = [":cake:",":moon_cake:",":cupcake:",":pancakes:"]
		await ctx.send(random.choice(emoji_choices))

	@commands.command(name='all', aliases=['a'])
	async def all_cake(self, ctx):
		embed = discord.Embed(title="All ·", colour=0xf7346b)
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
		for f, p in zip(getFriday(start, len(groups)), groups):
			p = "~~`"+p+"`~~" if date.today() >= f else "`"+p+"`"
			embed.add_field(name="Friday "+f.strftime("%d %B, %Y"), value=p.replace(' ', '` & `'), inline=False)
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='when', aliases=['w'])
	async def when_cake(self, ctx):
		name, status, pin = ctx.message.author.display_name.lower().replace('é', 'e').replace('-', ''), False, []
		for i, (f, p) in enumerate(zip(getFriday(start, len(groups)), groups)):
			if name in p.lower().replace('é', 'e').replace('-', '') and not pin: pin = [p, f]
		if not pin: raise commands.CommandError("member.isblacklisted")

		embed = discord.Embed(title="When ·", colour=0xf7346b)
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
		embed.add_field(name="`{}` be ready for the ".format(ctx.message.author.display_name), value="Friday "+pin[1].strftime("%d %B, %Y"), inline=False)
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.command(name='next', aliases=['n'])
	async def next_cake(self, ctx):
		pin = []
		for i, (f, p) in enumerate(zip(getFriday(start, len(groups)), groups)):
			if not date.today() >= f and not pin: pin = [p, f]
		embed = discord.Embed(title="Next ·", colour=0xf7346b)
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
		embed.add_field(name="The next cooks are :", value="`{}` for `Friday {}`".format(pin[0].replace(' ', '` et `'), pin[1].strftime("%d %B")), inline=False)
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
		await ctx.send(embed=embed)

	@when_cake.error
	async def when_cake_error(self, ctx, error):
		if str(error) == 'member.isblacklisted':
			await ctx.send("Sorry you're not participating in the Fridaycake event")
		else:
			await ctx.send('Error')

def setup(bot):
	bot.add_cog(FridayCake(bot))
