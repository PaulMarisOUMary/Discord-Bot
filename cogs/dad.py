import discord
import re

from discord.ext import commands
from random import random

from utils.basebot import DiscordBot


class Dad(commands.Cog, name="dad"):
    """
        Dad's jokes.
        
        Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
			- send_messages
    """
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        
        self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '👨‍🦳'
        label = "Dad's jokes"
        description = "Ahah, it was a good one!"
        return emoji, label, description

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message : discord.Message) -> None:
        if message.author.bot: 
            return

        content = message.content
        for joke in self.subconfig_data["jokes"]:
            regex = joke["regex"]
            response: str = joke["message"]
            probability = joke["probability"]

            pattern = re.compile(regex, re.VERBOSE + re.IGNORECASE)

            match = pattern.search(content)
            if match and random() <= probability:
                try:
                    format = response.format(content = content, bot = self.bot, match = match, value = match.group("value"))
                except:
                    format = response.format(content = content, bot = self.bot, match = match)

                await message.reply(format, mention_author=False)
                break


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Dad(bot))