import time
import discord

from discord.ext import commands

class Spotify(commands.Cog, name="spotify"):
	"""Spotify description"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='spotify', aliases=['sy', 'sp', 'spy', 'spot'])
	async def actual_calendar(self, ctx, user: discord.Member = None):
		keeper = True
		if user == None: user = ctx.author
		for activity in user.activities:
			if str(activity) == "Spotify":
				embed, keeper = discord.Embed(colour=activity.colour), False
				embed.set_author(name="Spotify", url="https://open.spotify.com/track/"+str(activity.track_id), icon_url="https://toppng.com/uploads/thumbnail//spotify-logo-icon-transparent-icon-spotify-11553501653zkfre5mcur.png")
				embed.add_field(name=activity.title, value=activity.artist, inline=False)
				embed.set_thumbnail(url=activity.album_cover_url)
				embed.set_footer(text=str(activity.duration)[2:-7]+" | Requested by : "+str(ctx.message.author.name)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.avatar_url)
				await ctx.send(embed=embed)
		if keeper: await ctx.send(str(user.name)+" is not currently listening to Spotify")

def setup(bot):
	bot.add_cog(Spotify(bot))
