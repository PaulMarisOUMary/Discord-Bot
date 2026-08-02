from typing import Any

from discord import Interaction, Member, User, app_commands
from discord.ext import commands

from models.sql import Me as MeModel
from utils.basetypes import GuildInteraction
from utils.bot import DiscordBot
from utils.checks import require_database
from utils.database import crud


@app_commands.guild_only()
class Me(
    commands.GroupCog,
    name="me",
    group_name="me",
    group_description="Like minecraft set your own /me !",
):
    """
    Like minecraft set your own /me !

    Require intents:
        - None

    Require bot permission:
        - None
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

    def help_custom(self) -> tuple[str, str, str]:
        return '🤙', "Me", "Set and show a brief description of yourself."

    @require_database(True)
    @app_commands.command(  # type: ignore
        name="set", description="Set your own brief description of yourself !"
    )
    @app_commands.describe(description="Your brief description of yourself.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def me(self, interaction: GuildInteraction, description: str) -> None:
        """Allows you to set or show a brief description of yourself."""

        max_length = self.subconfig["max_length"]
        if len(description) > max_length:
            raise commands.CommandError(
                f"The max-length of your *me* is set to: __{max_length}__ (yours is {len(description)})."
            )

        async with self.bot.get_database().session() as session:
            await crud.upsert(
                session,
                MeModel(
                    guild_id=interaction.guild.id,
                    user_id=interaction.user.id,
                    user_me=description,
                ),
            )
            await session.commit()

        await self.show_me_message(interaction, interaction.user)

    @app_commands.command(name="show", description="Show the /me of other users.")
    @app_commands.describe(user="The user you want to show the /me of.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def show_me(
        self,
        interaction: Interaction,
        user: Member | User | None = None,
    ) -> None:
        """Allows you to show the description of other users."""
        await self.show_me_message(interaction, user or interaction.user)

    async def show_me_message(
        self, interaction: Interaction, user: Member | User
    ) -> None:
        if not interaction.guild:
            await interaction.response.send_message(
                "This command must be used in a guild."
            )
            return

        if self.bot.database is None:
            await interaction.response.send_message(
                f"\u2022 **{user.display_name}** The database isn't available, descriptions are disabled."
            )
            return

        async with self.bot.database.session() as session:
            me = await session.get(MeModel, (interaction.guild.id, user.id))

        message = me.user_me if me and me.user_me else "No description provided.."
        await interaction.response.send_message(
            f"\u2022 **{user.display_name}** {message}"
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Me(bot))
