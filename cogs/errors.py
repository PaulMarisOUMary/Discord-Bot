import discord

from discord.ext import commands
from discord import app_commands
from logging import ERROR, CRITICAL

from utils.basebot import DiscordBot
from utils.errors import ErrorDispatcher


dispatcher = ErrorDispatcher()


@dispatcher.report_bug()
@dispatcher.register(app_commands.CommandInvokeError, commands.CommandInvokeError)
async def handle_command_invoke_error(error: app_commands.CommandInvokeError, responder) -> None:
    await responder(content=f"🕳️ Error: {error.original}")

# @dispatcher.register(app_commands.TransformerError)
# async def handle_transformer_error(error: app_commands.TransformerError, responder) -> None: ...

@dispatcher.report_bug()
@dispatcher.register(app_commands.TranslationError)
async def handle_translation_error(error: app_commands.TranslationError, responder) -> None:
    await responder(content=f"🕳️ Translation error: {error}")

@dispatcher.register(app_commands.NoPrivateMessage, commands.NoPrivateMessage)
async def handle_no_private_message(error: app_commands.NoPrivateMessage, responder) -> None:
    await responder(content="🕳️ This command cannot be used in DMs.")

@dispatcher.register(app_commands.MissingRole, commands.MissingRole)
async def handle_missing_role(error: app_commands.MissingRole, responder) -> None:
    await responder(content="🕳️ You are missing a required role to use this command.")

@dispatcher.register(app_commands.MissingAnyRole, commands.MissingAnyRole)
async def handle_missing_any_role(error: app_commands.MissingAnyRole, responder) -> None:
    await responder(content="🕳️ You are missing at least one of the required roles to use this command.")

@dispatcher.register(app_commands.MissingPermissions, commands.MissingPermissions)
async def handle_missing_permissions(error: app_commands.MissingPermissions, responder) -> None:
    await responder(content="🕳️ You are missing required permissions to use this command.")

@dispatcher.register(app_commands.BotMissingPermissions, commands.BotMissingPermissions)
async def handle_bot_missing_permissions(error: app_commands.BotMissingPermissions, responder) -> None:
    await responder(content="🕳️ I am missing required permissions to execute this command.")

@dispatcher.register(app_commands.CommandOnCooldown, commands.CommandOnCooldown)
async def handle_command_on_cooldown(error: app_commands.CommandOnCooldown, responder) -> None:
    await responder(content=f"🕳️ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")

# @dispatcher.register(app_commands.CommandLimitReached)
# async def handle_command_limit_reached(error: app_commands.CommandLimitReached, responder) -> None: ...

# @dispatcher.register(app_commands.CommandAlreadyRegistered)
# async def handle_command_already_registered(error: app_commands.CommandAlreadyRegistered, responder) -> None: ...

# @dispatcher.register(app_commands.CommandSignatureMismatch)
# async def handle_command_signature_mismatch(error: app_commands.CommandSignatureMismatch, responder) -> None: ...

# @dispatcher.register(app_commands.CommandNotFound)
# async def handle_command_not_found(error: app_commands.CommandNotFound, responder) -> None: ...

# @dispatcher.register(app_commands.MissingApplicationID)
# async def handle_missing_application_id(error: app_commands.MissingApplicationID, responder) -> None: ...

# @dispatcher.register(app_commands.CommandSyncFailure)
# async def handle_command_sync_failure(error: app_commands.CommandSyncFailure, responder) -> None: ...

# @dispatcher.register(commands.ConversionError)
# async def handle_conversion_error(error: commands.ConversionError, responder) -> None: ...

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
async def handle_max_concurrency_reached(error: commands.MaxConcurrencyReached, responder) -> None:
    await responder(content=f"🕳️ This command is already being used. Please wait until it is finished. {error.number}/{error.per}")


class Errors(commands.Cog, name="errors"):
    """Errors handler."""
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
    
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
            level = ERROR,
            exc_info = error,
        )

    @commands.Cog.listener("on_error")
    async def get_error(self, event, *args, **kwargs) -> None:
        """Error handler"""
        self.bot.log(
            message = f"Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.",
            name = "discord.get_error",
            level = CRITICAL,
        )

    @commands.Cog.listener("on_command_error")
    async def get_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """doc: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exception-hierarchy
        HybridCommands errors triggered by slash commands are passed to on_app_command_error.
        """

        if isinstance(error, commands.HybridCommandError):
            error = error.original
            if ctx.interaction:
                await self.get_app_command_error(ctx.interaction, error)
                return

        responder = ctx.send

        handled = await dispatcher.dispatch(error, responder)
        if not handled:
            self.trace_error("get_command_error", error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """doc: https://discordpy.readthedocs.io/en/latest/interactions/api.html#exception-hierarchy"""

        responder = interaction.response.send_message
        if interaction.response.is_done():
            responder = interaction.edit_original_response

        handled = await dispatcher.dispatch(error, responder)
        if not handled:
            self.trace_error("get_app_command_error", error)

    @commands.Cog.listener("on_view_error")
    async def get_view_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item) -> None:
        self.trace_error("get_view_error", error)

    @commands.Cog.listener("on_modal_error")
    async def get_modal_error(self, interaction: discord.Interaction, error: Exception) -> None:
        self.trace_error("get_modal_error", error)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Errors(bot))