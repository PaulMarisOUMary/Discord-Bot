import discord

from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from classes.ansi import Background as bg, Foreground as fg, Format as fmt
from classes.discordbot import DiscordBot
from views.helpmenu import View as HelpView

class HelpCommand(commands.HelpCommand):
    """Help command"""

    async def __get_contexted_app_command(self, ctx: commands.Context, target: app_commands.Command) -> Optional[Union[app_commands.AppCommand, app_commands.AppCommandGroup]]:
        tree_commands = await ctx.bot.tree.fetch_commands()
        for command in tree_commands:
            if not command.type == discord.AppCommandType.chat_input:
                continue

            for option in command.options:
                if isinstance(option, app_commands.AppCommandGroup):
                    if f"{command.name} {option.name}" == target.qualified_name:
                        return option

            if command.name == target.qualified_name:
                return command

    def __extend_group(self, group: Any, seen: Optional[List[Union[commands.Command, app_commands.Command, commands.HybridCommand]]] = None) -> List[Union[commands.Command, app_commands.Command, commands.HybridCommand]]:
        if not seen:
            seen = [group]
        for child in group.commands:
            if isinstance(child, (commands.Group, app_commands.Group, commands.HybridGroup)):
                seen.append(child) # type: ignore
                self.__extend_group(child, seen)
            else:
                seen.append(child)
        return seen

    def __remove_group_from_extended(self, extended_list: List[Union[commands.Command, app_commands.Command, commands.HybridCommand]]) -> List[Union[commands.Command, app_commands.Command, commands.HybridCommand]]:
        return [
            comand
            for comand in extended_list 
            if not isinstance(comand, (commands.Group, app_commands.Group))
        ]

    def __return_none_if_not(self, value: str) -> str:
        if not value:
            return "None"
        return value
    
    def __list_to_block(self, list: List[str], block: str = '`') -> str:
        if not list:
            return ''
        return f"{block}{f'{block} {block}'.join(list)}{block}"

    def __format_permissions(self, extras: dict):
        if not "bot_permissions" in extras or not extras["bot_permissions"]:
            return "None"
        return self.__list_to_block(extras['bot_permissions'], block='')
    
    async def __add_help_field_to_embed(self, embed: discord.Embed, command: Union[commands.Command, app_commands.Command, commands.HybridCommand], show_permissions: Optional[bool] = True):
        details = f"```ansi\n{fg.BLUE + fmt.UNDERLINE}Description{fmt.RESET}:\n"
        if isinstance(command, app_commands.Command):
            object = await self.__get_contexted_app_command(self.context, command)
            if not object:
                return
            command_mention = f"{object.mention} {self.__list_to_block([param for param in command._params.keys()])}"
            details += f"{fg.WHITE}{self.__return_none_if_not(object.description)}{fmt.RESET}"
        else:
            command_mention = f"{self.context.clean_prefix}{command.qualified_name} {self.__list_to_block([param for param in command.clean_params.keys()])}" 
            details += f"{fg.WHITE}{self.__return_none_if_not(command.description)}{fmt.RESET}"
        if show_permissions:
            details += f"\n{fg.CYAN + fmt.UNDERLINE}Required permissions{fmt.RESET}:\n{fg.GREY}{self.__format_permissions(command.extras)}{fmt.RESET}\n"
        embed.add_field(
            name=command_mention, 
            value=f"{details}\n```", 
            inline=False
        )

    def get_bot_mapping(self) -> Dict[Optional[commands.Cog], Union[List[commands.Command[Any, ..., Any]], List[app_commands.Command[Any, ..., Any]], List[commands.HybridCommand[Any, ..., Any]]]]:
        mapping = super().get_bot_mapping()

        compound_mapping: Dict[Optional[commands.Cog], Union[List[commands.Command[Any, ..., Any]], List[app_commands.Command[Any, ..., Any]], List[commands.HybridCommand[Any, ..., Any]]]] = mapping | dict()
        
        for command in self.context.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
            if isinstance(command, app_commands.Group): # Get only Subcommands
                continue

            if command.binding in mapping:
                compound_mapping[command.binding].append(command) # type: ignore
            else:
                compound_mapping[command.binding] = [command]

        return compound_mapping

    async def command_callback(self, ctx: commands.Context, *, command: Optional[str] = None):
        await self.prepare_help_command(ctx, command)

        bot = ctx.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)
        
        def from_cog(potential_cog: str) -> Optional[commands.Cog]:
            return bot.get_cog(potential_cog) 
        
        def from_command(potential_command: str) -> List[Union[commands.Command[Any, ..., Any], app_commands.Command[Any, ..., Any], commands.HybridCommand[Any, ..., Any]]]:
            mapping = self.get_bot_mapping()
            commands_found = list()
            for mapped_commands in mapping.values():
                for cmd in mapped_commands:
                    if cmd.name == potential_command:
                        commands_found.append(cmd)
            return commands_found
        
        def from_group(potential_group: str) -> Optional[app_commands.Group]:
            for cmd in self.context.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
                if isinstance(cmd, app_commands.Group) and cmd.name == potential_group:
                    return cmd

        keys = command.split(' ')
        is_keys = len(keys) > 1
        fkey = keys[0]

        if fkey == "cog" and is_keys:
            cog = from_cog(keys[1])
            if cog:
                return await self.send_cog_help(cog)
            else:
                return self.command_not_found(keys[1])
        elif fkey == "command" and is_keys:
            cmd = from_command(keys[1])
            if cmd:
                return await self.send_command_help(cmd)
            else:
                return self.command_not_found(keys[1])
        elif fkey == "group" and is_keys:
            group = from_group(keys[1])
            if group:
                return await self.send_group_help(group)
            else:
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

    async def send_bot_help(self, mapping: Dict[Optional[commands.Cog], Union[List[commands.Command[Any, ..., Any]], List[app_commands.Command[Any, ..., Any]], List[commands.HybridCommand[Any, ..., Any]]]]):
        allowed = 5
        close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))

        embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Home", description = f"`Welcome to the help page.`\n\n**The prefix on this server is**: `{self.context.clean_prefix}`.\n\nUse `{self.context.clean_prefix}help command <name>` for more info about a command.\nUse `{self.context.clean_prefix}help group <name>` for more info about a command group.\nUse `{self.context.clean_prefix}help cog <name>` for more info about a category.\nUse the dropdown menu below to select a category.\n\u200b", url='https://github.com/PaulMarisOUMary/Discord-Bot')
        embed.add_field(name="Time remaining :", value=f"This help session will end <t:{close_in}:R>.\nType `{self.context.clean_prefix}help` to open a new session.\n\u200b", inline=False)
        embed.add_field(name="Who am I ?", value="I'm a bot made by *WarriorMachine*.\nI have a lot of features !\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Discord-Bot) !")

        view = HelpView(timeout=allowed*60, context=self.context, mapping=mapping, homeembed=embed, ui=2)
        await self.context.send(embed = embed, view = view, delete_after=60*allowed)

    async def send_command_help(self, commands_list: List[Union[commands.Command[Any, ..., Any], app_commands.Command[Any, ..., Any], commands.HybridCommand[Any, ..., Any]]]):
        embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Commands", url = "https://github.com/PaulMarisOUMary/Discord-Bot")
        for command in commands_list:
            await self.__add_help_field_to_embed(embed, command)

        await self.context.send(embed = embed)

    async def send_cog_help(self, cog: commands.Cog):
        emoji = '👋'
        if hasattr(cog, "help_custom"):
            emoji, _, _ = cog.help_custom() # type: ignore
        embed = discord.Embed(color=discord.Color.dark_grey(), title = f"{emoji} Help · Cog", url = "https://github.com/PaulMarisOUMary/Discord-Bot")

        for command in cog.get_commands():
            await self.__add_help_field_to_embed(embed, command, False)
            if isinstance(command, commands.HybridCommand):
                await self.__add_help_field_to_embed(embed, command.app_command, False) # type: ignore

        for command in cog.__cog_app_commands__:
            await self.__add_help_field_to_embed(embed, command, False) # type: ignore

        await self.context.send(embed = embed)

    async def send_group_help(self, group: Union[commands.Group, app_commands.Group, commands.HybridGroup]):
        embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Group", url = "https://github.com/PaulMarisOUMary/Discord-Bot")
        embed.add_field(
                    name=f"Group: {group.name}", 
                    value=f"__Description__:\n*{self.__return_none_if_not(group.description)}*", 
                    inline=False
                )
        subcommands = self.__remove_group_from_extended(self.__extend_group(group))
        for command in subcommands:
            await self.__add_help_field_to_embed(embed, command)

        await self.context.send(embed = embed)

    def command_not_found(self, string: str):
        raise commands.CommandNotFound(f"`{string}` not found !")

    async def on_help_command_error(self, _: commands.Context, error):
        handledErrors = [
            commands.CommandOnCooldown, 
            commands.CommandNotFound
        ]

        if not type(error) in handledErrors:
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
            "cooldown": commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
            #"hidden": True,
            "name": "help",
        } 

        bot.help_command = HelpCommand(command_attrs=attributes)
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '🆘'
        label = "Help"
        description = "Help utilities."
        return emoji, label, description

async def setup(bot: DiscordBot):
	await bot.add_cog(Help(bot))