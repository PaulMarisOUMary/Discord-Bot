import io
import time
import discord
import matplotlib.pyplot as plt

from discord.ext import commands

def statServer(guild):
	status = {}
	must = ['members', 'bot', 'streaming', 'idle', 'dnd', 'online', 'offline', 'mobile']
	for a in must:
		status[a] = 0
	for member in guild:
		status['members'] += 1
		status[str(member.status)] += 1
		if member.is_on_mobile(): status['mobile'] += 1
		if member.bot: status['bot'] += 1
		if member.activity or member.activities: 
			for activity in member.activities:
				if activity.type == discord.ActivityType.streaming:
					status['streaming'] += 1

	return status

class Info(commands.Cog, name="info", command_attrs=dict(hidden=False)):
	"""Info & statistics"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='stat', aliases=['status','graph','gs','sg'])
	async def stat(self, ctx):
		"""Show a graphic pie about the server's members""" 
		plt.clf()
		ax, data, colors = plt.subplot(), statServer(ctx.guild.members), ["#747f8d","#f04747","#faa81a","#43b582"]
		ax.pie([data['offline'], data['dnd'], data['idle'], data['online']], colors=colors, startangle=-40, wedgeprops=dict(width=0.5))
		leg = ax.legend(['Offline','dnd','idle','Online'],frameon=False, loc='lower center', ncol=5)
		for color,text in zip(colors,leg.get_texts()):
			text.set_color(color)
		image_binary = io.BytesIO()
		plt.savefig(image_binary, transparent=True)
		image_binary.seek(0)
		
		embed = discord.Embed(title="Current server stats ({})".format(data['members']),description="<:offline:698246924138184836> : **`{}`** (Offline)\n<:idle:698246924058361898> : **`{}`** (AFK)\n<:dnd:698246924528254986> : **`{}`** (dnd)\n<:online:698246924465340497> : **`{}`** (Online)\n<:streaming:699381397898395688> : **`{}`** (Streaming)\n<:phone0:698257015578951750> : **`{}`** (on mobile)\n<:isbot:698250069165473852> : **`{}`** (Robot)".format(data['offline'], data['idle'], data['dnd'], data['online'], data['streaming'], data['mobile'], data['bot']))
		embed.set_image(url='attachment://stat.png')
		embed.set_footer(text="Requested by : "+str(ctx.message.author)+" at "+str(time.strftime('%H:%M:%S')), icon_url=ctx.message.author.display_avatar.url)
		await ctx.send(file=discord.File(fp=image_binary, filename='stat.png'), embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))
