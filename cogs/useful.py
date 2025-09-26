import discord

from discord.ext import commands

from utils.ansi import Format as fmt, Foreground as fg, Background as bg
from utils.basebot import DiscordBot
from utils.helper import bot_has_permissions
from utils.basetypes import GuildContext


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

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '🚩'
		label = "Useful"
		description = "Useful commands."
		return emoji, label, description

	@commands.command(name="emojilist", aliases=["ce", "el"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	async def getcustomemojis(self, ctx: GuildContext) -> None:
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
	async def codeblock_colors(self, ctx: commands.Context) -> None:
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
	@commands.guild_only()
	async def cleanup(self, ctx: GuildContext, n_message: int) -> None:
		if n_message < 1 or n_message > 150:
			raise ValueError("Invalid number of messages to delete.")

		if self.bot.use_database:
			prefix = self.bot.prefixes[ctx.guild.id]
		else:
			prefix = self.bot.__prefix_default

		def check(message: discord.Message):
			return (message.author == ctx.me or message.content.startswith(prefix)) and not (message.mentions or message.role_mentions)

		deleted = await ctx.channel.purge(limit=n_message, check=check, before=ctx.message)
		
		await ctx.message.reply(content=f"🗑️ Deleted {len(deleted)} messages.", delete_after=5, mention_author=False)


async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Useful(bot))
