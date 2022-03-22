import discord
import asyncio

from discord.ext import commands
from datetime import datetime, timedelta
from views import help as vhelp

class HelpCommand(commands.HelpCommand):
    """Help command"""

    async def on_help_command_error(self, ctx, error) -> None:
        handledErrors = [
            commands.CommandOnCooldown, 
            commands.CommandNotFound
        ]

        if not type(error) in handledErrors:
            print("! Help command Error :", error, type(error), type(error).__name__)
            return await super().on_help_command_error(ctx, error)

    def command_not_found(self, string) -> None:
        raise commands.CommandNotFound(f"Command {string} is not found")

    async def send_bot_help(self, mapping) -> None:
        allowed = 5
        close_in = round(datetime.timestamp(datetime.now() + timedelta(minutes=allowed)))
        embed = discord.Embed(color=discord.Color.dark_grey(), title = "👋 Help · Home", description = f"`Welcome to the help page.`\n\n**The prefix on this server is**: `{self.context.clean_prefix}`.\n\nUse `help command` for more info on a command.\nUse `help category` for more info on a category.\nUse the dropdown menu below to select a category.\n\u200b", url='https://github.com/PaulMarisOUMary/Algosup-Discord')
        embed.add_field(name="Time remaining :", value=f"This help session will end <t:{close_in}:R>.\nType `help` to open a new session.\n\u200b", inline=False)
        embed.add_field(name="Who am I ?", value="I'm a bot made by *WarriorMachine*. Made for Algosup in 2020.\nI have a lot of features such translator, events manager, utils, and more.\n\nI'm open source, you can see my code on [Github](https://github.com/PaulMarisOUMary/Algosup-Discord) !")

        view = vhelp.View(mapping = mapping, ctx = self.context, homeembed = embed, ui = 2)
        message = await self.context.send(embed = embed, view = view)
        try:
            await asyncio.sleep(60*allowed)
            view.stop()
            await message.delete()
            await self.context.message.add_reaction("<a:checkmark_a:842800730049871892>")
        except: 
            pass

    async def send_command_help(self, command):
        cog = command.cog
        if "help_custom" in dir(cog):
            emoji, label, _ = cog.help_custom()
            embed = discord.Embed(title = f"{emoji} Help · {label} : {command.name}", description=f"**Command** : {command.name}\n{command.help}", url="https://github.com/PaulMarisOUMary/Algosup-Discord")
            params = ""
            for param in command.clean_params: 
                params += f" <{param}>"
            embed.add_field(name="Usage", value=f"{command.name}{params}", inline=False)
            embed.add_field(name="Aliases", value=f"{command.aliases}`")
            embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=self.context.message.author.display_avatar.url)
            await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        if "help_custom" in dir(cog):
            emoji, label, _ = cog.help_custom()
            embed = discord.Embed(title = f"{emoji} Help · {label}",description=f"`{cog.__doc__}`", url="https://github.com/PaulMarisOUMary/Algosup-Discord")
            for command in cog.get_commands():
                params = ""
                for param in command.clean_params: 
                    params += f" <{param}>"
                embed.add_field(name=f"{command.name}{params}", value=f"{command.help}\n\u200b", inline=False)
            embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=self.context.message.author.display_avatar.url)
            await self.context.send(embed=embed)

    async def send_group_help(self, group):
        await self.context.send("Group commands unavailable.")

class Help(commands.Cog, name="help"):
    """Help commands."""
    def __init__(self, bot: commands.Bot) -> None:
        self._original_help_command = bot.help_command

        attributes = {
            'name': "help",
            'aliases': ['h', '?'],
            'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user) # discordpy2.0
        } 

        bot.help_command = HelpCommand(command_attrs=attributes)
        bot.help_command.cog = self
        
    def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    def help_custom(self) -> tuple[str]:
        emoji = '🆘'
        label = "Help"
        description = "Help utilities."
        return emoji, label, description

async def setup(bot):
	await bot.add_cog(Help(bot))