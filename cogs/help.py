import discord

from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional, Union

from views.helpmenu import View as HelpView
from classes.discordbot import DiscordBot

class HelpCommand(commands.HelpCommand):
    """Help command"""

    def get_bot_mapping(self) -> dict[Optional[commands.Cog], list[Union[commands.Command, app_commands.Command]]]:
        mapping = super().get_bot_mapping()
        
        for command in self.context.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
            if hasattr(command, "binding"):
                if command.binding is None: # type: ignore
                    continue

                if command.binding in mapping: # type: ignore
                    mapping[command.binding].append(command) # type: ignore
                else:
                    mapping[command.binding] = [command] # type: ignore

        return mapping # type: ignore

    async def on_help_command_error(self, ctx, error):
        handledErrors = [
            commands.CommandOnCooldown, 
            commands.CommandNotFound
        ]

        if not type(error) in handledErrors:
            print("! Help command Error :", error, type(error), type(error).__name__)
            return await super().on_help_command_error(ctx, error)

    def command_not_found(self, string: str):
        raise commands.CommandNotFound(f"Command {string} is not found")

    async def send_bot_help(self, mapping: dict[Optional[commands.Cog], list[Union[commands.Command, app_commands.Command]]]):
        allowed = 5
        close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))

        embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Home", description = f"`Welcome to the help page.`\n\n**The prefix on this server is**: `{self.context.clean_prefix}`.\n\nUse `{self.context.clean_prefix}help command` for more info on a command.\nUse `{self.context.clean_prefix}help category` for more info on a category.\nUse the dropdown menu below to select a category.\n\u200b", url='https://github.com/PaulMarisOUMary/Discord-Bot')
        embed.add_field(name="Time remaining :", value=f"This help session will end <t:{close_in}:R>.\nType `{self.context.clean_prefix}help` to open a new session.\n\u200b", inline=False)
        embed.add_field(name="Who am I ?", value="I'm a bot made by *WarriorMachine*.\nI have a lot of features !\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Discord-Bot) !")

        view = HelpView(timeout=allowed*60, context=self.context, mapping=mapping, homeembed=embed, ui=2)
        await self.context.send(embed = embed, view = view, delete_after=60*allowed)

    async def send_command_help(self, command: commands.Command):
        pass # Not implemented

    async def send_cog_help(self, cog):
        pass # Not implemented

    async def send_group_help(self, group):
        await self.context.send("Group commands unavailable.")

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
            "name": "help",
            "aliases": ['h', '?'],
            "cooldown": commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)
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