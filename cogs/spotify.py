from discord import Embed, Interaction, Member, User, app_commands
from discord import Spotify as dSpotify
from discord.ext import commands
from discord.utils import utcnow

from utils.bot import DiscordBot
from utils.checks import bot_has_permissions


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

    @bot_has_permissions(send_messages=True)
    @app_commands.command(
        name="spotify", description="Display the current Spotify status."
    )
    @app_commands.describe(user="The user to get Spotify information from.")
    @app_commands.guild_only()
    async def spotify_activity(
        self, interaction: Interaction, user: Member | User | None
    ) -> None:
        """Show the current Spotify song."""
        target = user or interaction.user

        member = interaction.guild.get_member(target.id)  # type: ignore

        if not member:
            await interaction.response.send_message(
                "Could not fetch this user.", ephemeral=True
            )
            return

        spotify = next(
            (act for act in member.activities if isinstance(act, dSpotify)), None
        )

        if not spotify:
            await interaction.response.send_message(
                f"{member.display_name} does not listen to Spotify."
            )
            return

        minutes, seconds = divmod(int(spotify.duration.total_seconds()), 60)
        duration_fmt = f"{minutes}:{seconds:02d}"

        embed = Embed(
            title=spotify.title,
            url=spotify.track_url,
            colour=spotify.color,
            timestamp=utcnow(),
        )
        embed.set_thumbnail(url=spotify.album_cover_url)
        embed.add_field(name="Artist", value=", ".join(spotify.artists), inline=True)
        embed.add_field(name="Album", value=spotify.album, inline=True)
        embed.set_footer(
            text=f"Duration: {duration_fmt} | Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Spotify(bot))
