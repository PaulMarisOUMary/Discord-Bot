from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from discord import AppCommandType, Color, Embed, app_commands
from discord.ext import commands

from utils.ansi import Background as bg
from utils.ansi import Foreground as fg
from utils.ansi import Format as fmt
from utils.basetypes import CommandLike, GroupLike, HasHelpCustom

REPO_URL = "https://github.com/PaulMarisOUMary/Discord-Bot"


class HelpEngine:
    def __init__(self, ctx: commands.Context) -> None:
        self.ctx = ctx
        self._tree_commands_cache: list[app_commands.AppCommand] | None = None

    async def _contexted_app_commands(self) -> list[app_commands.AppCommand]:
        if self._tree_commands_cache is None:
            self._tree_commands_cache = await self.ctx.bot.tree.fetch_commands()
        return self._tree_commands_cache

    async def _get_contexted_app_command(
        self, target: app_commands.Command
    ) -> app_commands.AppCommand | app_commands.AppCommandGroup | None:
        for command in await self._contexted_app_commands():
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

    @staticmethod
    def get_description(command: CommandLike | Any) -> str | None:
        description = getattr(command, "description", None)
        if description:
            return description

        if hasattr(command, "help") and isinstance(command.help, str):
            return command.help

        if hasattr(command, "callback") and command.callback.__doc__:
            return command.callback.__doc__

        return None

    @staticmethod
    def extend_group(
        group: GroupLike, seen: list[CommandLike | GroupLike] | None = None
    ) -> list[CommandLike | GroupLike]:
        if seen is None:
            seen = [group]

        for child in group.commands:
            seen.append(child)
            if isinstance(
                child, (commands.Group, app_commands.Group, commands.HybridGroup)
            ):
                HelpEngine.extend_group(child, seen)

        return seen

    @staticmethod
    def remove_groups(extended: list[CommandLike | GroupLike]) -> list[CommandLike]:
        return [
            command
            for command in extended
            if not isinstance(command, (commands.Group, app_commands.Group))
        ]

    @staticmethod
    def return_none_if_not(value: str | None) -> str:
        return value if value else "None"

    @staticmethod
    def list_to_block(values: list[str], block: str = "`") -> str:
        if not values:
            return ""
        return f"{block}{f'{block} {block}'.join(values)}{block}"

    @classmethod
    def format_permissions(cls, extras: dict[str, Any]) -> str:
        permissions = extras.get("bot_permissions")
        if not permissions:
            return "None"
        return cls.list_to_block(permissions, block="")

    async def add_field(
        self, embed: Embed, command: CommandLike, show_permissions: bool = True
    ) -> None:
        details = f"```ansi\n{fg.BLUE + fmt.UNDERLINE}Description{fmt.RESET}:\n"
        mentions: list[str] = []

        if isinstance(command, app_commands.Command):
            contexted = await self._get_contexted_app_command(command)
            if not contexted:
                return
            mentions.append(
                f"{contexted.mention} {self.list_to_block(list(command._params.keys()))}"
            )
            desc = self.get_description(contexted) or self.get_description(command)
            details += f"{fg.WHITE}{self.return_none_if_not(desc)}{fmt.RESET}"
        else:
            mentions.append(
                f"{self.ctx.clean_prefix}{command.qualified_name} {self.list_to_block(list(command.clean_params.keys()))}"
            )
            desc = self.get_description(command)
            details += f"{fg.WHITE}{self.return_none_if_not(desc)}{fmt.RESET}"

            if isinstance(command, commands.HybridCommand) and command.app_command:
                contexted = await self._get_contexted_app_command(command.app_command)
                if contexted:
                    mentions.append(
                        f"{contexted.mention} {self.list_to_block(list(command.app_command._params.keys()))}"
                    )

        if show_permissions:
            details += f"\n{fg.RED + fmt.UNDERLINE}Required permissions{fmt.RESET}:\n{bg.BLACK}{self.format_permissions(command.extras)}{fmt.RESET}\n"

        embed.add_field(name='\n'.join(mentions), value=f"{details}\n```", inline=False)

    def get_compound_mapping(self) -> dict[commands.Cog | None, list[CommandLike]]:
        bot = self.ctx.bot
        mapping: dict[commands.Cog | None, list[CommandLike]] = {
            cog: list(cog.get_commands()) for cog in bot.cogs.values()
        }
        mapping[None] = [command for command in bot.commands if command.cog is None]

        hybrid_qualified_names = {
            command.qualified_name
            for commands_list in mapping.values()
            for command in commands_list
            if isinstance(command, commands.HybridCommand)
        }

        for command in bot.tree.walk_commands(type=AppCommandType.chat_input):
            if isinstance(command, app_commands.Group):
                continue
            if command.qualified_name in hybrid_qualified_names:
                continue

            mapping.setdefault(command.binding, [])
            mapping[command.binding].append(command)

        return {cog: cmds for cog, cmds in mapping.items() if cmds}

    async def build_home_embed(self) -> Embed:
        ctx = self.ctx
        allowed = 5
        close_in = round(
            datetime.timestamp(datetime.now() + timedelta(minutes=allowed))
        )

        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Home",
            description=(
                "`Welcome to the help page.`\n\n"
                f"**The prefix on this server is**: `{ctx.clean_prefix}`.\n\n"
                f"Use `{ctx.clean_prefix}help command <name>` for more info about a command.\n"
                f"Use `{ctx.clean_prefix}help group <name>` for more info about a command group.\n"
                f"Use `{ctx.clean_prefix}help cog <name>` for more info about a category.\n"
                "Use the dropdown menu below to select a category.\n\u200b"
            ),
            url=REPO_URL,
        )
        embed.add_field(
            name="Time remaining :",
            value=f"This help session will end <t:{close_in}:R>.\nType `{ctx.clean_prefix}help` to open a new session.\n\u200b",
            inline=False,
        )
        embed.add_field(
            name="Who am I ?",
            value="I'm a bot made by [@WarriorMachine](https://discord.com/users/265148938091233293).\nI have a lot of features !\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Discord-Bot) !",
        )
        return embed

    async def build_command_embed(self, commands_list: list[CommandLike]) -> Embed:
        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Commands",
            url=REPO_URL,
        )
        for command in commands_list:
            await self.add_field(embed, command)
        return embed

    async def build_cog_embed(self, cog: commands.Cog) -> Embed:
        emoji, label, description = '👋', cog.qualified_name, cog.description
        if isinstance(cog, HasHelpCustom):
            emoji, label, description = cog.help_custom()

        embed = Embed(
            color=Color.dark_grey(),
            title=f"{emoji} Help \xb7 Cog",
            description=f"\xb7 **{label}**\n{description}",
            url=REPO_URL,
        )

        for command in cog.get_commands():
            await self.add_field(embed, command, False)

        for app_command in cog.__cog_app_commands__:
            if isinstance(app_command, app_commands.Group):
                continue
            await self.add_field(embed, app_command, False)

        return embed

    async def build_group_embed(self, group: GroupLike) -> Embed:
        embed = Embed(
            color=Color.dark_grey(),
            title="👋 Help \xb7 Group",
            url=REPO_URL,
        )
        embed.add_field(
            name=f"Group: {group.name}",
            value=f"__Description__:\n*{self.return_none_if_not(group.description)}*",
            inline=False,
        )

        for command in self.remove_groups(self.extend_group(group)):
            await self.add_field(embed, command)

        return embed
