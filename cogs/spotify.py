import discord
import time

from discord.utils import get
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union

from utils.basebot import DiscordBot
from utils.helper import bot_has_permissions


class Spotify(commands.Cog, name="spotify"):
	"""
		Show Spotify presence on discord.
	
		Require intents:
			- presences
		
		Require bot permission:
			- use_external_emojis
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '🎶'
		label = "Spotify"
		description = "Spotify player status commands."
		return emoji, label, description

	@bot_has_permissions(embed_links=True)
	@app_commands.command(name="spotify")
	@app_commands.describe(user="The user to get spotify informations from.")
	async def spotify_activity(self, interaction: discord.Interaction, user: Optional[Union[discord.Member, discord.User]]) -> None:
		"""Show the current Spotify song."""
		if not user: 
			user = interaction.user
		realuser = get(self.bot.get_all_members(), id=user.id)
		if not realuser:
			await interaction.response.send_message("User not found.", ephemeral=True)
			return
		for activity in realuser.activities:
			if isinstance(activity, discord.activity.Spotify):
				embed = discord.Embed(colour=activity.colour)
				embed.set_author(name="Spotify", url=f"https://open.spotify.com/track/{activity.track_id}", icon_url="https://toppng.com/uploads/thumbnail//spotify-logo-icon-transparent-icon-spotify-11553501653zkfre5mcur.png")
				embed.add_field(name=activity.title, value=activity.artist, inline=False)
				embed.set_thumbnail(url=activity.album_cover_url)
				embed.set_footer(text=f"{str(activity.duration)[2:-7]} | Requested by : {interaction.user.name} at {time.strftime('%H:%M:%S')}", icon_url=interaction.user.display_avatar.url)
				await interaction.response.send_message(embed=embed)
				return
		
		await interaction.response.send_message(f"{user.name} is not currently listening to Spotify")


async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Spotify(bot))