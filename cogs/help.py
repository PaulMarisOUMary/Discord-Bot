from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, NoReturn

from discord import AppCommandType, Color, Embed, Interaction, app_commands
from discord.errors import Forbidden
from discord.ext import commands

from utils.ansi import Foreground as fg
from utils.ansi import Format as fmt
from utils.basetypes import CommandLike, GroupLike, HasHelpCustom
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions
from views.helpmenu import View as HelpView


class HelpCommand(commands.HelpCommand):
    """Help command"""

    def __init__(self, **options: Any) -> None:
        super().__init__(**options)
        self._tree_commands_cache: list[app_commands.AppCommand] | None = None

    async def __contexted_app_commands(self) -> list[app_commands.AppCommand]:
        if self._tree_commands_cache is None:
            self._tree_commands_cache = await self.context.bot.tree.fetch_commands()
        return self._tree_commands_cache

    async def __get_contexted_app_command(
        self, target: app_commands.Command
    ) -> app_commands.AppCommand | app_commands.AppCommandGroup | None:
        for command in await self.__contexted_app_commands():
            if command.type != AppCommandType.chat_input:
                continue

            for option in command.options:
                if (
                    isinstance(option, app_commands.AppCommandGroup)
                    and f"{command.name} {option.name}" == target.qualified_name
                ):
                    return option

            if command.name == target.qualified_name:
                return command

        return None

    def __extend_group(
        self, group: GroupLike, seen: list[CommandLike | GroupLike] | None = None
    ) -> list[CommandLike | GroupLike]:
        if seen is None:
            seen = [group]

        for child in group.commands:
            seen.append(child)
            if isinstance(
                child, (commands.Group, app_commands.Group, commands.HybridGroup)
            ):
                self.__extend_group(child, seen)

        return seen

    def __remove_group_from_extended(
        self, extended_list: list[CommandLike | GroupLike]
    ) -> list[CommandLike]:
        return [
            command
            for command in extended_list
            if not isinstance(command, (commands.Group, app_commands.Group))
        ]

    def __return_none_if_not(self, value: str | None) -> str:
        return value if value else "None"

    def __list_to_block(self, values: list[str], block: str = "`") -> str:
        if not values:
            return ""
        return f"{block}{f'{block} {block}'.join(values)}{block}"

    def __format_permissions(self, extras: dict[str, Any]) -> str:
        permissions = extras.get("bot_permissions")
        if not permissions:
            return "None"
        return self.__list_to_block(permissions, block="")

    async def __add_help_field_to_embed(
        self, embed: Embed, command: CommandLike, show_permissions: bool = True
    ) -> None:
        details = f"```ansi\n{fg.BLUE + fmt.UNDERLINE}Description{fmt.RESET}:\n"

        if isinstance(command, app_commands.Command):
            contexted = await self.__get_contexted_app_command(command)
            if not contexted:
                return
            command_mention = f"{contexted.mention} {self.__list_to_block(list(command._params.keys()))}"
            details += f"{fg.WHITE}{self.__return_none_if_not(contexted.description)}{fmt.RESET}"
        else:
            command_mention = f"{self.context.clean_prefix}{command.qualified_name} {self.__list_to_block(list(command.clean_params.keys()))}"
            details += (
                f"{fg.WHITE}{self.__return_none_if_not(command.description)}{fmt.RESET}"
            )

        if show_permissions:
            details += f"\n{fg.CYAN + fmt.UNDERLINE}Required permissions{fmt.RESET}:\n{fg.GREY}{self.__format_permissions(command.extras)}{fmt.RESET}\n"

        embed.add_field(name=command_mention, value=f"{details}\n```", inline=False)

    def filter_mapping(self, mapping: dict[Any, list[Any]]) -> dict[Any, list[Any]]:
        return {key: values for key, values in mapping.items() if values}

    def get_bot_mapping(self) -> dict[commands.Cog | None, list[CommandLike]]:  # ty: ignore[invalid-method-override]
        mapping = super().get_bot_mapping()
        compound_mapping: dict[commands.Cog | None, list[CommandLike]] = {
            cog: list(cog_commands) for cog, cog_commands in mapping.items()
        }

        for command in self.context.bot.tree.walk_commands(
            type=AppCommandType.chat_input
        ):
            if isinstance(command, app_commands.Group):
                continue

            compound_mapping.setdefault(command.binding, [])
            compound_mapping[command.binding].append(command)

        return self.filter_mapping(compound_mapping)

    async def command_callback(
        self, ctx: commands.Context, *, command: str | None = None
    ) -> None:
        await self.prepare_help_command(ctx, command)

        bot = ctx.bot

        if command is None:
            return await self.send_bot_help(self.get_bot_mapping())

        def from_cog(potential_cog: str) -> commands.Cog | None:
            return bot.get_cog(potential_cog)

        def from_command(potential_command: str) -> list[CommandLike]:
            mapping = self.get_bot_mapping()
            return [
                cmd
                for mapped_commands in mapping.values()
                for cmd in mapped_commands
                if cmd.name == potential_command
            ]

        def from_group(potential_group: str) -> app_commands.Group | None:
            for cmd in self.context.bot.tree.walk_commands(
                type=AppCommandType.chat_input
            ):
                if isinstance(cmd, app_commands.Group) and cmd.name == potential_group:
                    return cmd
            return None

        keys = command.split(" ")
        is_keys = len(keys) > 1
        fkey = keys[0]

        if fkey == "cog" and is_keys:
            cog = from_cog(keys[1])
            if cog:
                return await self.send_cog_help(cog)
            return self.command_not_found(keys[1])
        elif fkey == "command" and is_keys:
            commands_found = from_command(keys[1])
            if commands_found:
                return await self.send_command_help(commands_found)
            return self.command_not_found(keys[1])
        elif fkey == "group" and is_keys:
            group = from_group(keys[1])
            if group:
                return await self.send_group_help(group)
            return self.command_not_found(keys[1])

        cog = from_cog(command)
        if cog:
            return await self.send_cog_help(cog)

        commands_found = from_command(command)
        if commands_found:
            return await self.send_command_help(commands_found)

        group = from_group(command)
        if group:
            return await self.send_group_help(group)

        return self.command_not_found(keys[0])

    async def send_bot_help(
        self, mapping: dict[commands.Cog | None, list[CommandLike]], /
    ) -> None:  # ty: ignore[invalid-method-override]
        allowed = 5
        close_in = round(
            datetime.timestamp(datetime.now() + timedelta(minutes=allowed))
        )

        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Home",
            description=(
                "`Welcome to the help page.`\n\n"
                f"**The prefix on this server is**: `{self.context.clean_prefix}`.\n\n"
                f"Use `{self.context.clean_prefix}help command <name>` for more info about a command.\n"
                f"Use `{self.context.clean_prefix}help group <name>` for more info about a command group.\n"
                f"Use `{self.context.clean_prefix}help cog <name>` for more info about a category.\n"
                "Use the dropdown menu below to select a category.\n\u200b"
            ),
            url="https://github.com/PaulMarisOUMary/Discord-Bot",
        )
        embed.add_field(
            name="Time remaining :",
            value=f"This help session will end <t:{close_in}:R>.\nType `{self.context.clean_prefix}help` to open a new session.\n\u200b",
            inline=False,
        )
        embed.add_field(
            name="Who am I ?",
            value="I'm a bot made by *WarriorMachine*.\nI have a lot of features !\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Discord-Bot) !",
        )

        view = HelpView(mapping=mapping, help_object=self, home_embed=embed)
        await self.context.send(embed=embed, view=view, delete_after=60 * allowed)

    async def send_command_help(self, commands_list: list[CommandLike], /) -> None:  # ty: ignore[invalid-method-override]
        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Commands",
            url="https://github.com/PaulMarisOUMary/Discord-Bot",
        )
        for command in commands_list:
            await self.__add_help_field_to_embed(embed, command)

        await self.context.send(embed=embed)

    async def build_cog_embed(self, cog: commands.Cog) -> Embed:
        emoji, label, description = "👋", cog.qualified_name, cog.description
        if isinstance(cog, HasHelpCustom):
            emoji, label, description = cog.help_custom()

        embed = Embed(
            color=Color.dark_grey(),
            title=f"{emoji} Help \xb7 Cog",
            description=f"\xb7 **{label}**\n{description}",
            url="https://github.com/PaulMarisOUMary/Discord-Bot",
        )

        for command in cog.get_commands():
            await self.__add_help_field_to_embed(embed, command, False)
            if isinstance(command, commands.HybridCommand) and command.app_command:
                await self.__add_help_field_to_embed(embed, command.app_command, False)

        for app_command in cog.__cog_app_commands__:
            if isinstance(app_command, app_commands.Group):
                continue
            await self.__add_help_field_to_embed(embed, app_command, False)

        return embed

    async def send_cog_help(self, cog: commands.Cog, /) -> None:
        await self.context.send(embed=await self.build_cog_embed(cog))

    async def send_group_help(self, group: GroupLike) -> None:
        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Group",
            url="https://github.com/PaulMarisOUMary/Discord-Bot",
        )
        embed.add_field(
            name=f"Group: {group.name}",
            value=f"__Description__:\n*{self.__return_none_if_not(group.description)}*",
            inline=False,
        )

        subcommands = self.__remove_group_from_extended(self.__extend_group(group))
        for command in subcommands:
            await self.__add_help_field_to_embed(embed, command)

        await self.context.send(embed=embed)

    def command_not_found(self, string: str) -> NoReturn:
        raise commands.CommandNotFound(f"`{string}` not found !")

    _HANDLED_HELP_ERRORS = (
        commands.CommandOnCooldown,
        commands.CommandNotFound,
        Forbidden,
    )

    async def on_help_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if not isinstance(error, self._HANDLED_HELP_ERRORS):
            raise error


class Help(commands.Cog, name="help"):
    """
    Help commands.

    Require intents:
        - message_content

    Require bot permission:
        - read_messages
        - send_messages
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self._original_help_command = bot.help_command

        attributes = {
            "aliases": ['h', '?'],
            "cooldown": commands.CooldownMapping.from_cooldown(
                1, 5, commands.BucketType.user
            ),
            "name": "help",
        }

        help_command = HelpCommand(command_attrs=attributes)
        help_command.cog = self
        bot.help_command = help_command

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    def help_custom(self) -> tuple[str, str, str]:
        return '🆘', "Help", "Help utilities."

    @bot_has_permissions(send_messages=True)
    @app_commands.command(name="help", description="Help command.")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def help(self, interaction: Interaction[DiscordBot]) -> None:
        context = await commands.Context.from_interaction(interaction)
        await context.send_help()


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Help(bot))
