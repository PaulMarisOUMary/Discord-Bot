import discord
import asyncio

from datetime import datetime, timedelta

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

class Usefull(commands.Cog, name="usefull"):
	"""
		Usefull commands for Devs & more.

		Require intents:
			- message_content
		
		Require bot permission:
			- send_messages
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	"""def help_custom(self) -> tuple[str]:
		emoji = '🚩'
		label = "Usefull"
		description = "Usefull commands."
		return emoji, label, description"""

	@app_commands.command(name="reminder", description="Reminds you of something.")
	@app_commands.describe(hours="Hours.", minutes="Minutes.", seconds="Seconds.", message="Your reminder message.")
	@app_commands.choices(hours=[Choice(name=str(i), value=i) for i in range(0, 25)], minutes=[Choice(name=str(i), value=i) for i in range(0, 56, 5)], seconds=[Choice(name=str(i), value=i) for i in range(5, 56, 5)])
	@app_commands.checks.bot_has_permissions(send_messages=True)
	@app_commands.checks.has_permissions(use_slash_commands=True)
	async def reminder(self, interaction: discord.Interaction, hours: int, minutes: int, seconds: int, message: str) -> None:
		"""Reminds you of something."""
		remind_in = round(datetime.timestamp(datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)))
		await interaction.response.send_message(f"Your message will be sent <t:{remind_in}:R>.")
		
		await asyncio.sleep(seconds+minutes*60+hours*(60**2))
		await interaction.channel.send(f":bell: <@{interaction.user.id}> Reminder (<t:{remind_in}:R>): {message}")

	@app_commands.command(name="strawpoll", description="Create a strawpoll.")
	@app_commands.describe(question="The question of the strawpoll.")
	@app_commands.checks.has_permissions(use_slash_commands=True)
	async def avatar(self, interaction: discord.Interaction, question: str):
		await interaction.response.send_message(content=f"__*{interaction.user.mention}*__ : {question}", allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False))
		message = await interaction.original_message()
		await message.add_reaction("<a:checkmark_a:842800730049871892>")
		await message.add_reaction("<a:crossmark:842800737221607474>")

	@commands.command(name="emojilist", aliases=["ce", "el"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	async def getcustomemojis(self, ctx):
		"""Return a list of each cutom emojis from the current server."""
		embed_list, embed = [], discord.Embed(title=f"Custom Emojis List ({len(ctx.guild.emojis)}) :")
		for i, emoji in enumerate(ctx.guild.emojis, start=1):
			if i == 0 : 
				i += 1
			value = f"`<:{emoji.name}:{emoji.id}>`" if not emoji.animated else f"`<a:{emoji.name}:{emoji.id}>`"
			embed.add_field(name=f"{self.bot.get_emoji(emoji.id)} - **:{emoji.name}:** - (*{i}*)",value=value)
			if len(embed.fields) == 25:
				embed_list.append(embed)
				embed = discord.Embed()
		if len(embed.fields) > 0: 
			embed_list.append(embed)

		for message in embed_list:
			await ctx.send(embed=message)



async def setup(bot):
	await bot.add_cog(Usefull(bot))
