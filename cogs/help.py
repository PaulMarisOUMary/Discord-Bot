from __future__ import annotations

from discord import AppCommandType, app_commands
from discord.ext import commands

from utils.basetypes import CommandLike
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions
from utils.helpengine import HelpEngine
from views.helpmenu import View as HelpView


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
        bot.help_command = None

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    def help_custom(self) -> tuple[str, str, str]:
        return '🆘', "Help", "Help utilities."

    def command_not_found(self, string: str) -> None:
        raise commands.CommandNotFound(f"Command `{string}` not found !")

    @bot_has_permissions(send_messages=True)
    @commands.hybrid_command(
        name="help", aliases=['h', '?'], description="Help command."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx: commands.Context, *, query: str | None = None) -> None:
        engine = HelpEngine(ctx)

        if query is None:
            embed = await engine.build_home_embed()
            view = HelpView(
                mapping=engine.get_compound_mapping(), engine=engine, home_embed=embed
            )
            await ctx.send(embed=embed, view=view, delete_after=60 * 5)
            return

        keys = query.split(' ')
        is_keys = len(keys) > 1
        fkey = keys[0]

        def from_cog(potential_cog: str) -> commands.Cog | None:
            return ctx.bot.get_cog(potential_cog)

        def from_command(potential_command: str) -> list[CommandLike]:
            mapping = engine.get_compound_mapping()
            return [
                cmd
                for mapped_commands in mapping.values()
                for cmd in mapped_commands
                if cmd.name == potential_command
            ]

        def from_group(potential_group: str) -> app_commands.Group | None:
            for cmd in ctx.bot.tree.walk_commands(type=AppCommandType.chat_input):
                if isinstance(cmd, app_commands.Group) and cmd.name == potential_group:
                    return cmd
            return None

        if fkey == "cog" and is_keys:
            cog = from_cog(keys[1])
            if not cog:
                return self.command_not_found(keys[1])
            await ctx.send(embed=await engine.build_cog_embed(cog))
            return

        if fkey == "command" and is_keys:
            commands_found = from_command(keys[1])
            if not commands_found:
                return self.command_not_found(keys[1])
            await ctx.send(embed=await engine.build_command_embed(commands_found))
            return

        if fkey == "group" and is_keys:
            group = from_group(keys[1])
            if not group:
                return self.command_not_found(keys[1])
            await ctx.send(embed=await engine.build_group_embed(group))
            return

        cog = from_cog(query)
        if cog:
            await ctx.send(embed=await engine.build_cog_embed(cog))
            return

        commands_found = from_command(query)
        if commands_found:
            await ctx.send(embed=await engine.build_command_embed(commands_found))
            return

        group = from_group(query)
        if group:
            await ctx.send(embed=await engine.build_group_embed(group))
            return

        self.command_not_found(keys[0])


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Help(bot))
