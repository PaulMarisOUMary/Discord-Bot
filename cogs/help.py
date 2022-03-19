import discord
import asyncio

from discord.ext import commands
from datetime import datetime, timedelta
from views import help as vhelp #need big refactor

class MyHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    def command_not_found(self, string):
        return super().command_not_found(string)

    def subcommand_not_found(self, command, string):
        return super().subcommand_not_found(command, string)

    async def send_error_message(self, error):
        return await super().send_error_message(error)

    async def on_help_command_error(self, ctx, error):
        print("! Help command Error :", error, type(error), type(error).__name__)
        return await super().on_help_command_error(ctx, error)

    async def send_bot_help(self, mapping): #mapping = all commands by cogs (dict) : {cog: [cmd, cmd]}
        await self.context.send("Help")

    async def send_command_help(self, command):
        await self.context.send("This is help command")

    async def send_group_help(self, group):
        await self.context.send("This is help group")

    async def send_cog_help(self, cog):
        await self.context.send("This is help cog")

class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self._original_help_command = bot.help_command

        attributes = {
            'name': "help",
            'aliases': ['h', '?'],
            'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user) #discordpy2.0
        } 

        bot.help_command = MyHelpCommand(command_attrs=attributes)
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
	bot.add_cog(Help(bot))