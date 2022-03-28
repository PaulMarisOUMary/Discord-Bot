import io
import time
import discord
import matplotlib.pyplot as plt

from datetime import datetime
from discord.ext import commands
from discord import app_commands

def statServer(guild) -> dict:
	status = {}
	must = ["members", "bot", "streaming", "idle", "dnd", "online", "offline", "mobile"]
	for a in must:
		status[a] = 0
	for member in guild:
		status["members"] += 1
		status[str(member.status)] += 1
		if member.is_on_mobile(): 
			status["mobile"] += 1
		if member.bot: 
			status["bot"] += 1
		if member.activity or member.activities: 
			for activity in member.activities:
				if activity.type == discord.ActivityType.streaming:
					status["streaming"] += 1

	return status

class Info(commands.Cog, name="info"):
	"""Info & statistics."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str]:
		emoji = '📊'
		label = "Info"
		description = "Commands about additionals informations such as stats."
		return emoji, label, description

	@commands.command(name="stat", aliases=["status","graph","gs","sg"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	async def stat(self, ctx):
		"""Show a graphic pie about the server's members.""" 
		plt.clf()
		ax, data, colors = plt.subplot(), statServer(ctx.guild.members), ["#747f8d","#f04747","#faa81a","#43b582"]
		ax.pie([data["offline"], data["dnd"], data["idle"], data["online"]], colors=colors, startangle=-40, wedgeprops=dict(width=0.5))
		leg = ax.legend(["Offline","dnd","idle","Online"],frameon=False, loc="lower center", ncol=5)
		for color,text in zip(colors,leg.get_texts()):
			text.set_color(color)
		image_binary = io.BytesIO()
		plt.savefig(image_binary, transparent=True)
		image_binary.seek(0)
		
		embed = discord.Embed(title=f"Current server stats ({data['members']})",description=f"<:offline:698246924138184836> : **`{data['offline']}`** (Offline)\n<:idle:698246924058361898> : **`{data['idle']}`** (AFK)\n<:dnd:698246924528254986> : **`{data['dnd']}`** (dnd)\n<:online:698246924465340497> : **`{data['online']}`** (Online)\n<:streaming:699381397898395688> : **`{data['streaming']}`** (Streaming)\n<:phone:948279755248111756> : **`{data['mobile']}`** (on mobile)\n<:isbot:698250069165473852> : **`{data['bot']}`** (Robot)")
		embed.set_image(url="attachment://stat.png")
		embed.set_footer(text=f"Requested by : {ctx.message.author} at {time.strftime('%H:%M:%S')}", icon_url=ctx.message.author.display_avatar.url)
		await ctx.send(file=discord.File(fp=image_binary, filename="stat.png"), embed=embed)

	@app_commands.command(name="avatar", description="Display the avatar.")
	@app_commands.describe(user="The user to get the avatar from.")
	@app_commands.guilds(discord.Object(id=332234497078853644))
	async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
		if not user:
			user = interaction.user
		await interaction.response.send_message(user.display_avatar.url)

	@app_commands.command(name="banner", description="Display the banner.")
	@app_commands.describe(user="The user to get the banner from.")
	@app_commands.guilds(discord.Object(id=332234497078853644))
	async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
		if not user: 
			user = interaction.user
		user = await self.bot.fetch_user(user.id)
		try:
			await interaction.response.send_message(user.banner.url)
		except:
			await interaction.response.send_message("This user doesn't have a banner.")

	@commands.command(name="lookup", aliases=["lk"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	async def lookup(self, ctx, member: discord.Member = None):
		"""Show few information about a discord Member"""
		if not member: 
			member = ctx.author

		try:
			user = await self.bot.fetch_user(member.id)
			user_banner = user.banner.url
		except: 
			user_banner = None

		yes = "<a:checkmark_a:842800730049871892>"
		no = "<a:crossmark:842800737221607474>"

		embed=discord.Embed(color=member.color)
		embed.set_author(name=f"Lookup: {member.display_name}", icon_url=member.default_avatar.url)
		embed.add_field(name="ID:", value=f"`{member.id}`", inline=True)
		embed.add_field(name="Display name:", value=f"`{member.name}#{member.discriminator}`", inline=True)
		if member.status == discord.Status.online: 
			embed.add_field(name="Status", value=f"<:online:698246924465340497> Online", inline=True)
		elif member.status == discord.Status.idle: 
			embed.add_field(name="Status", value=f"<:idle:698246924058361898> Idle", inline=True)
		elif member.status == discord.Status.dnd: 
			embed.add_field(name="Status", value=f"<:dnd:698246924528254986> Do not disturb", inline=True)
		else: 
			embed.add_field(name="Status", value=f"<:offline:698246924138184836> Offline", inline=True)
		embed.add_field(name="\u200b", value="\u200b", inline=False)
		embed.add_field(name="<:isbot:698250069165473852> Is a bot?", value=f"{yes if member.bot else no}", inline=True)
		embed.add_field(name="<:phone:948279755248111756> Is on mobile?", value=f"{yes if member.is_on_mobile() else no}", inline=True)
		embed.add_field(name="<a:nitro:948271095566434357> Is a booster?", value=f"<t:{round(datetime.timestamp(member.premium_since))}:F>" if member.premium_since else no, inline=True)
		embed.add_field(name="\u200b", value="\u200b", inline=False)
		embed.add_field(name="<:plus:948272417304883270> Account created at:", value=f"<t:{round(datetime.timestamp(member.created_at))}:F>", inline=True)
		embed.add_field(name="<:join:948272122353057792> Joined the server at:", value=f"<t:{round(datetime.timestamp(member.joined_at))}:F>", inline=True)
		embed.set_thumbnail(url=member.display_avatar.url)
		if user_banner: 
			embed.set_image(url=user_banner)
		embed.set_footer(text=f"(The discord profile picture next to the 'lookup' text is your default profile picture.)\nRequested by : {ctx.message.author} at {time.strftime('%H:%M:%S')}", icon_url=ctx.message.author.display_avatar.url)
		await ctx.send(embed=embed)



async def setup(bot):
	await bot.add_cog(Info(bot))
