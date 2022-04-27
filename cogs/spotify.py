import time
import discord

from discord.utils import get
from discord.ext import commands
from discord import app_commands

class Spotify(commands.Cog, name="spotify"):
	"""
		Show Spotify presence on discord.
	
		Require intents:
			- presences
		
		Require bot permission:
			- use_external_emojis
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = "<:spotify:880896591756656641>"
		label = "Spotify"
		description = "Spotify status commands."
		return emoji, label, description

	@app_commands.command(name="spotify")
	@app_commands.describe(user="The user to get spotify informations from.")
	@app_commands.checks.has_permissions(use_slash_commands=True)
	async def spotify_activity(self, interaction: discord.Interaction, user: discord.Member = None):
		"""Show the current Spotify song."""
		if not user: 
			user = interaction.user
		realuser = get(self.bot.get_all_members(), id=user.id)
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



async def setup(bot):
	await bot.add_cog(Spotify(bot))