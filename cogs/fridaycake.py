import time
import random
import discord

from datetime import date, timedelta
from discord.ext import commands

groups = ["Aurélien Romain", "Théo Salah", "Louis Clémentine", "Paul Martin", "Karine Laura-Lee", "Max Clément", "Brendon Eloi", "Florent Ivan", "Laurent"]
holidays = [(date(2021, 6, 30), date(2021, 9, 23))]
start = date(2021, 5, 14) #year #month #day


def getFriday(date, holiday, count):
    holes, i = [], 0
    date += timedelta(days=4 - date.weekday())
    for h in holiday:
        hole = h[0]+timedelta(days=1 - h[0].weekday())
        for _ in range(h[0].toordinal(), h[1].toordinal()+1):
            hole += timedelta(days=1)
            holes.append(hole)
    while i <= count:
        if not date in holes:
            yield date
            i += 1
        date += timedelta(days=7)


class FridayCake(commands.Cog, name="fridaycake", command_attrs=dict(hidden=False)):
    """FridayCake's commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cake', aliases=['fc'])
    async def cake(self, ctx):
        """Show a random emoji of cake :)"""
        emoji_choices = [":cake:", ":moon_cake:", ":cupcake:", ":pancakes:"]
        await ctx.send(random.choice(emoji_choices))

    @commands.command(name='fridaycakeinfo', aliases=['fci'])
    async def cake(self, ctx):
        """Explain how the order of participants is made"""
        await ctx.send("FridayCake : *The order of the participants on the list has been generated randomly, your date is resulted of chaos.*")

    @commands.command(name='all', aliases=['a'])
    async def all_cake(self, ctx):
        """Show the complete order list for the FridayCake event"""
        embed = discord.Embed(title="All ·", colour=0xf7346b)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
        for f, p in zip(getFriday(start, holidays, len(groups)), groups):
            p = "~~`"+p+"`~~" if date.today() >= f else "`"+p+"`"
            embed.add_field(name="Friday "+f.strftime("%d %B, %Y"),
                            value=p.replace(' ', '` & `'), inline=False)
        embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at " +
                        str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='when', aliases=['w'])
    async def when_cake(self, ctx):
        """Show your specific date about the FridayCake event"""
        name, pin = ctx.message.author.display_name.lower().replace(
            'é', 'e').replace('-', ''), []
        for _, (f, p) in enumerate(zip(getFriday(start, holidays, len(groups)), groups)):
            if name in p.lower().replace('é', 'e').replace('-', '') and not pin:
                pin = [p, f]
        if not pin:
            raise commands.CommandError("member.isblacklisted")

        embed = discord.Embed(title="When ·", colour=0xf7346b)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
        embed.add_field(name="`{}` be ready for the ".format(
            ctx.message.author.display_name), value="Friday "+pin[1].strftime("%d %B, %Y"), inline=False)
        embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at " +
                        str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='next', aliases=['n'])
    async def next_cake(self, ctx):
        """Show who are the next to make a cake for the FridayCake event"""
        pin = []
        for i, (f, p) in enumerate(zip(getFriday(start, holidays, len(groups)), groups)):
            if not date.today() >= f and not pin:
                pin = [p, f]
        embed = discord.Embed(title="Next ·", colour=0xf7346b)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
        embed.add_field(name="The next cooks are :", value="`{}` for `Friday {}`".format(
            pin[0].replace(' ', '` & `'), pin[1].strftime("%d %B")), inline=False)
        embed.set_footer(text="Requested by : "+str(ctx.message.author.name)+" at " +
                        str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    @when_cake.error
    async def when_cake_error(self, ctx, error):
        if str(error) == 'member.isblacklisted':
            await ctx.send("Sorry you're not participating in the Fridaycake event")
        else:
            await ctx.send('Error')


def setup(bot):
    bot.add_cog(FridayCake(bot))
