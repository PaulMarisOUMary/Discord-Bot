from logging import CRITICAL, ERROR, getLogger
from typing import Any, cast

from discord import Interaction, app_commands
from discord.ext import commands
from discord.ui import Item

from utils.bot import DiscordBot
from utils.errors import ErrorDispatcher

_log = getLogger(__name__)

dispatcher = ErrorDispatcher()


@dispatcher.report_bug()
@dispatcher.register(app_commands.CommandInvokeError, commands.CommandInvokeError)
async def handle_command_invoke_error(
    error: app_commands.CommandInvokeError | commands.CommandInvokeError, responder
) -> None:
    await responder(content=f"🕳️ Error: {error.original}")


@dispatcher.report_bug()
@dispatcher.register(app_commands.TranslationError)
async def handle_translation_error(
    error: app_commands.TranslationError, responder
) -> None:
    await responder(content=f"🕳️ Translation error: {error}")


@dispatcher.register(app_commands.NoPrivateMessage, commands.NoPrivateMessage)
async def handle_no_private_message(
    error: app_commands.NoPrivateMessage | commands.NoPrivateMessage, responder
) -> None:
    await responder(content="🕳️ This command cannot be used in DMs.")


@dispatcher.register(app_commands.MissingRole, commands.MissingRole)
async def handle_missing_role(
    error: app_commands.MissingRole | commands.MissingRole, responder
) -> None:
    await responder(content="🕳️ You are missing a required role to use this command.")


@dispatcher.register(app_commands.MissingAnyRole, commands.MissingAnyRole)
async def handle_missing_any_role(
    error: app_commands.MissingAnyRole | commands.MissingAnyRole, responder
) -> None:
    await responder(
        content="🕳️ You are missing at least one of the required roles to use this command."
    )


@dispatcher.register(app_commands.MissingPermissions, commands.MissingPermissions)
async def handle_missing_permissions(
    error: app_commands.MissingPermissions | commands.MissingPermissions, responder
) -> None:
    await responder(
        content="🕳️ You are missing required permissions to use this command."
    )


@dispatcher.register(app_commands.BotMissingPermissions, commands.BotMissingPermissions)
async def handle_bot_missing_permissions(
    error: app_commands.BotMissingPermissions | commands.BotMissingPermissions,
    responder,
) -> None:
    await responder(
        content="🕳️ I am missing required permissions to execute this command."
    )


@dispatcher.register(app_commands.CommandOnCooldown, commands.CommandOnCooldown)
async def handle_command_on_cooldown(
    error: app_commands.CommandOnCooldown | commands.CommandOnCooldown, responder
) -> None:
    await responder(
        content=f"🕳️ This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@dispatcher.register(commands.UserInputError)
async def handle_user_input_error(error: commands.UserInputError, responder) -> None:
    await responder(content=f"🕳️ {error}")


@dispatcher.register(commands.CommandNotFound)
async def handle_command_not_found(error: commands.CommandNotFound, responder) -> None:
    await responder(content=f"🕳️ Command `{str(error).split(' ')[1]}` not found !")


@dispatcher.register(commands.CheckFailure)
async def handle_check_failure(error: commands.CheckFailure, responder) -> None:
    await responder(content=f"🕳️ {error}")


@dispatcher.register(commands.DisabledCommand)
async def handle_disabled_command(error: commands.DisabledCommand, responder) -> None:
    await responder(content="🕳️ Sorry this command is disabled.")


@dispatcher.register(commands.MaxConcurrencyReached)
async def handle_max_concurrency_reached(
    error: commands.MaxConcurrencyReached, responder
) -> None:
    await responder(
        content=f"🕳️ This command is already being used. Please wait until it is finished. {error.number}/{error.per}"
    )


class Errors(commands.Cog, name="errors"):
    """Errors handler."""

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = cast(Any, self.__dispatch_to_app_command_handler)

    async def cog_unload(self) -> None:
        self.bot.tree.on_error = cast(Any, self._old_tree_error)

    async def __dispatch_to_app_command_handler(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        self.bot.dispatch("app_command_error", interaction, error)

    def trace_error(self, name: str, error: Exception) -> None:
        getLogger(f"{__name__}.{name}").log(ERROR, type(error).__name__, exc_info=error)

    @commands.Cog.listener("on_error")
    async def get_error(self, event: str, *args: object, **kwargs: object) -> None:
        """Uncaught error in a plain (non-command) event listener."""
        _log.log(
            CRITICAL,
            f"Unexpected internal error: (event) {event}, (args) {args}, (kwargs) {kwargs}.",
        )

    @commands.Cog.listener("on_command_error")
    async def get_command_error(
        self, ctx: commands.Context[DiscordBot], error: commands.CommandError
    ) -> None:
        """
        doc: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exception-hierarchy
        HybridCommand errors triggered by slash commands are passed to on_app_command_error.
        """
        if isinstance(error, commands.HybridCommandError):
            original = error.original
            if ctx.interaction and isinstance(original, app_commands.AppCommandError):
                await self.get_app_command_error(ctx.interaction, original)
                return

        handled = await dispatcher.dispatch(error, ctx.send)
        if not handled:
            self.trace_error("get_command_error", error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        """doc: https://discordpy.readthedocs.io/en/latest/interactions/api.html#exception-hierarchy"""
        responder = interaction.response.send_message
        if interaction.response.is_done():
            responder = interaction.edit_original_response

        handled = await dispatcher.dispatch(error, responder)
        if not handled:
            self.trace_error("get_app_command_error", error)

    @commands.Cog.listener("on_view_error")
    async def get_view_error(
        self, interaction: Interaction, error: Exception, item: Item
    ) -> None:
        self.trace_error("get_view_error", error)

    @commands.Cog.listener("on_modal_error")
    async def get_modal_error(self, interaction: Interaction, error: Exception) -> None:
        self.trace_error("get_modal_error", error)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Errors(bot))
