import discord
import asyncio

from datetime import datetime, timedelta

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from classes.ansi import Format as fmt, Foreground as fg, Background as bg
from classes.discordbot import DiscordBot
from classes.utilities import bot_has_permissions

class Useful(commands.Cog, name="useful"):
	"""
		Usefull commands for Devs & more.

		Require intents:
			- message_content
		
		Require bot permission:
			- send_messages
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	"""def help_custom(self) -> tuple[str]:
		emoji = '🚩'
		label = "Useful"
		description = "Useful commands."
		return emoji, label, description"""

	@bot_has_permissions(send_messages=True)
	@app_commands.command(name="reminder", description="Reminds you of something.")
	@app_commands.describe(hours="Hours.", minutes="Minutes.", seconds="Seconds.", message="Your reminder message.")
	@app_commands.choices(hours=[Choice(name=str(i), value=i) for i in range(0, 25)], minutes=[Choice(name=str(i), value=i) for i in range(0, 56, 5)], seconds=[Choice(name=str(i), value=i) for i in range(5, 56, 5)])
	async def reminder(self, interaction: discord.Interaction, hours: int, minutes: int, seconds: int, message: str) -> None:
		"""Reminds you of something."""
		remind_in = round(datetime.timestamp(datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)))
		await interaction.response.send_message(f"Your message will be sent <t:{remind_in}:R>.")
		
		await asyncio.sleep(seconds+minutes*60+hours*(60**2))
		await interaction.channel.send(f":bell: <@{interaction.user.id}> Reminder (<t:{remind_in}:R>): {message}")

	@app_commands.command(name="strawpoll", description="Create a strawpoll.")
	@app_commands.describe(question="The question of the strawpoll.")
	async def avatar(self, interaction: discord.Interaction, question: str):
		await interaction.response.send_message(content=f"__*{interaction.user.mention}*__ : {question}", allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False))
		message = await interaction.original_response()
		await message.add_reaction("<a:checkmark_a:842800730049871892>")
		await message.add_reaction("<a:crossmark:842800737221607474>")

	@commands.command(name="emojilist", aliases=["ce", "el"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	async def getcustomemojis(self, ctx):
		"""Return a list of each custom emojis from the current server."""
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

	@commands.command(name="colors")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def codeblock_colors(self, ctx: commands.Context):
		codeblock = "```ansi\n"

		for item, text in [
			(fmt._member_map_, "Format"),
			(fg._member_map_, "Foreground"),
			(bg._member_map_, "Background")
		]:
			codeblock += f"{fmt.UNDERLINE + fg.GRAY + bg.WHITE}{text}{fmt.RESET}:\n"
			for key, value in item.items():
				codeblock += f"ESC[{value.value}m {value}{key}{fmt.RESET}\n"

		await ctx.send(f"{codeblock}```")

	@bot_has_permissions(manage_messages=True, read_message_history=True)
	@commands.command(name="cleanup")
	async def cleanup(self, ctx: commands.Context, n_message: int):
		if n_message < 1 or n_message > 150:
			raise ValueError("Invalid number of messages to delete.")

		prefix = self.bot.prefixes[ctx.guild.id]

		def check(message: discord.Message):
			return (message.author == ctx.me or message.content.startswith(prefix)) and not (message.mentions or message.role_mentions)

		deleted = await ctx.channel.purge(limit=n_message, check=check, before=ctx.message)
		
		await ctx.message.reply(content=f"🗑️ Deleted {len(deleted)} messages.", delete_after=5, mention_author=False)



async def setup(bot: DiscordBot):
	await bot.add_cog(Useful(bot))
