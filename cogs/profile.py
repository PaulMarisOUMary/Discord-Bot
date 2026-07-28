from logging import getLogger

from discord import Interaction, Member, User, app_commands
from discord.ext import commands

from utils.bot import DiscordBot
from utils.checks import bot_has_permissions

_log = getLogger(__name__)


class Profile(commands.Cog, name="profile"):
    """
    Profile commands.

    Require intents:
        - members
        - presences

    Require bot permission:
        - use_external_emojis
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @bot_has_permissions(send_messages=True)
    @app_commands.command(name="avatar", description="Display the avatar.")
    @app_commands.describe(
        user="The user to get the avatar from.", main="If true, shows the main avatar."
    )
    async def avatar(
        self, interaction: Interaction, user: Member | User | None, main: bool = False
    ):
        target = user or interaction.user

        avatar = (
            (target.avatar or target.default_avatar) if main else target.display_avatar
        )

        await interaction.response.send_message(avatar.url)

    @bot_has_permissions(send_messages=True)
    @app_commands.command(name="banner", description="Display the avatar.")
    @app_commands.describe(
        user="The user to get the banner from.", main="If true, shows the main banner."
    )
    async def banner(
        self, interaction: Interaction, user: Member | User | None, main: bool = False
    ):
        target = user or interaction.user

        banner = (
            target.display_banner
            if not main and isinstance(target, Member)
            else target.banner
        )

        if banner is None:
            fetched_user = await interaction.client.fetch_user(target.id)
            banner = fetched_user.banner

        if not banner:
            await interaction.response.send_message("This user doesn't have a banner.")
            return

        await interaction.response.send_message(banner.url)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Profile(bot))
