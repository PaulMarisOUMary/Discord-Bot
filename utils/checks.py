from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeVar, cast

from discord import Interaction, Permissions, app_commands
from discord.ext import commands

from utils.bot import DiscordBot

if TYPE_CHECKING:
    from discord.permissions import _PermissionsKwargs
    from typing_extensions import Unpack

CommandLike = commands.Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]
RawCallback = Callable[..., Coroutine[Any, Any, Any]]
Decoratable = TypeVar("Decoratable", bound=CommandLike | RawCallback)


class DatabaseRequirementNotMet(commands.CheckFailure, app_commands.CheckFailure):
    def __init__(self, require: bool) -> None:
        self.require = require

        message = f"This command requires the database to be {'enabled' if require else 'disabled'}."
        super().__init__(message)


def require_database(require: bool = True) -> Callable[[Decoratable], Decoratable]:
    def classic_predicate(ctx: commands.Context[DiscordBot]) -> bool:
        if ctx.bot.config.bot.use_database != require:
            raise DatabaseRequirementNotMet(require)
        return True

    def app_predicate(interaction: Interaction[DiscordBot]) -> bool:
        client = interaction.client

        if client.config.bot.use_database != require:
            raise DatabaseRequirementNotMet(require)
        return True

    def decorator(command: Decoratable) -> Decoratable:
        # already a built command object
        if isinstance(command, commands.Command):
            command.checks.append(classic_predicate)

            app_command = getattr(command, "app_command", None)
            if app_command is not None:
                app_command.checks.append(app_predicate)

            return command

        if isinstance(command, app_commands.Command):
            command.checks.append(app_predicate)
            return command

        # raw callback
        func = cast(Any, command)

        if not hasattr(func, "__commands_checks__"):
            func.__commands_checks__ = []
        func.__commands_checks__.append(classic_predicate)

        if not hasattr(func, "__discord_app_commands_checks__"):
            func.__discord_app_commands_checks__ = []
        func.__discord_app_commands_checks__.append(app_predicate)

        return command

    return decorator


def bot_has_permissions(
    **perms: Unpack[_PermissionsKwargs],
) -> Callable[[Decoratable], Decoratable]:
    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    required_perms = [perm for perm, value in perms.items() if value]

    def record_extras(target: CommandLike) -> None:
        existing = target.extras.setdefault("bot_permissions", [])
        target.extras["bot_permissions"] = list(
            dict.fromkeys([*existing, *required_perms])
        )

    def decorator(command: Decoratable) -> Decoratable:
        # already a built command object
        if isinstance(command, commands.Command):
            commands.bot_has_permissions(**perms)(command)
            record_extras(command)

            app_command = getattr(command, "app_command", None)
            if app_command is not None:
                app_commands.checks.bot_has_permissions(**perms)(app_command)
                record_extras(app_command)

            return command

        if isinstance(command, app_commands.Command):
            app_commands.checks.bot_has_permissions(**perms)(command)
            record_extras(command)
            return command

        # raw callback
        func = commands.bot_has_permissions(**perms)(command)
        func = app_commands.checks.bot_has_permissions(**perms)(func)

        return func

    return decorator
