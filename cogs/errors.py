import discord

from discord.ext import commands
from discord import app_commands
from logging import ERROR as LOG_ERROR, CRITICAL as LOG_CRITICAL

from utils.basebot import DiscordBot


class Errors(commands.Cog, name="errors"):
    """Errors handler."""
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.default_error_message = "🕳️ There is an error."
    
    async def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.__dispatch_to_app_command_handler

    async def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        self.bot.dispatch("app_command_error", interaction, error)

    def trace_error(self, level: str, error: Exception) -> None:
        self.bot.log(
            message = type(error).__name__,
            name = f"discord.{level}",
            level = LOG_ERROR,
            exc_info = error,
        )

    async def __respond_to_interaction(self, interaction: discord.Interaction) -> bool:
        try:
            await interaction.response.send_message(content=self.default_error_message, ephemeral=True)
            return True
        except discord.errors.InteractionResponded:
            return False

    @commands.Cog.listener("on_error")
    async def get_error(self, event, *args, **kwargs) -> None:
        """Error handler"""
        self.bot.log(
            message = f"Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.",
            name = "discord.get_error",
            level = LOG_CRITICAL,
        )

    @commands.Cog.listener("on_command_error")
    async def get_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """doc: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exception-hierarchy"""
        self.trace_error("get_command_error", error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """doc: https://discordpy.readthedocs.io/en/latest/interactions/api.html#exception-hierarchy"""
        self.trace_error("get_app_command_error", error)

    @commands.Cog.listener("on_view_error")
    async def get_view_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item) -> None:
        self.trace_error("get_view_error", error)

    @commands.Cog.listener("on_modal_error")
    async def get_modal_error(self, interaction: discord.Interaction, error: Exception) -> None:
        self.trace_error("get_modal_error", error)

        if not isinstance(error, discord.errors.Forbidden):
            raise error


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Errors(bot))