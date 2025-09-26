import discord

from discord.ext import commands
from discord import app_commands
from typing import Optional, Union

from utils.basebot import DiscordBot
from utils.helper import bot_has_permissions


class Info(commands.Cog, name="info"):
	"""
		Info & statistics.
	
		Require intents: 
			- members
			- presences
		
		Require bot permission:
			- use_external_emojis
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '📊'
		label = "Info"
		description = "Commands about additionals informations such as stats."
		return emoji, label, description

	@bot_has_permissions(embed_links=True)
	@app_commands.command(name="avatar", description="Display the avatar.")
	@app_commands.describe(user="The user to get the avatar from.")
	async def avatar(self, interaction: discord.Interaction, user: Optional[Union[discord.Member, discord.User]]) -> None:
		if not user:
			user = interaction.user

		if isinstance(user, discord.Member):
			avatar = user.guild_avatar or user.avatar
		else:
			avatar = user.avatar

		await interaction.response.send_message(avatar.url)

	@bot_has_permissions(embed_links=True)
	@app_commands.command(name="banner", description="Display the banner.")
	@app_commands.describe(user="The user to get the banner from.")
	async def banner(self, interaction: discord.Interaction, user: Optional[Union[discord.Member, discord.User]]) -> None:
		if not user: 
			user = interaction.user

		if isinstance(user, discord.Member):
			banner = user.guild_banner or user.banner
		else:
			banner = user.banner

		if not banner:
			await interaction.response.send_message("This user doesn't have a banner.")

		await interaction.response.send_message(banner.url)


async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Info(bot))