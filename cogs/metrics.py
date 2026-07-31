from typing import Any

from discord import Interaction, InteractionType, Member, User, app_commands
from discord.ext import commands
from discord.ext.commands.hybrid import HybridAppCommand

from models.sql import Metric
from utils.bot import DiscordBot
from utils.database import crud


class Metrics(commands.Cog, name="metrics"):
    """
        Store bot's metrics in the database.
        For statistics and analytics.

        Require intents:
            - None

        Require bot permission:
            - None
    """
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[self.__cog_name__.lower()]

    def help_custom(self) -> tuple[str, str, str]:
        return '📈', "Metrics", "All metrics related to the bot."

    @commands.Cog.listener("on_command")
    async def on_command(self, context: commands.Context) -> None:
        if context.interaction or context.command is None:
            return

        if isinstance(context.command, commands.HybridCommand):
            await self.add_metrics(context.command.qualified_name, "commands.HybridCommand", context.author)
        elif isinstance(context.command, commands.Command):
            await self.add_metrics(context.command.qualified_name, "commands.Command", context.author)

    @commands.Cog.listener("on_interaction")
    async def on_interaction(self, interaction: Interaction) -> None:
        if interaction.type != InteractionType.application_command or interaction.command is None:
            return

        if isinstance(interaction.command, HybridAppCommand):
            await self.add_metrics(interaction.command.qualified_name, "commands.HybridCommand", interaction.user)
        elif isinstance(interaction.command, app_commands.Command):
            await self.add_metrics(interaction.command.qualified_name, "application_commands.Command", interaction.user)

    async def add_metrics(self, command_name: str, command_type: str, invoker: Member | User) -> None:
        """Add a metric to the database."""
        if self.bot.database is None:
            return

        if self.bot.owner_ids and invoker.id in self.bot.owner_ids:
            return
        if self.bot.owner_id and invoker.id == self.bot.owner_id:
            return

        async with self.bot.database.session() as session:
            await crud.increment(
                session,
                Metric,
                {"command_name": command_name, "command_type": command_type},
                "command_count",
            )
            await session.commit()


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Metrics(bot))