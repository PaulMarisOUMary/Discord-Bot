from random import random
from re import IGNORECASE, VERBOSE, compile

import discord
from discord.ext import commands

from utils.bot import DiscordBot


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

        self.subconfig = self.bot.config.cogs.cogs[self.__cog_name__.lower()]

        self.jokes: list[dict] = [
            {
                "pattern": compile(joke["regex"], VERBOSE + IGNORECASE),
                "message": joke["message"],
                "probability": joke.get("probability", 1.0),
            }
            for joke in self.subconfig.get("jokes", [])
        ]

    def help_custom(self) -> tuple[str, str, str]:
        return '👨‍🦳', "Dad's jokes", "Nearly collapsed from peak comedy. Call an ambulance!"

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content

        for joke in self.jokes:
            match = joke["pattern"].search(content)

            if match and random() <= joke["probability"]:
                groups = match.groupdict()
                value = groups.get("value") or (
                    match.group(1) if match.groups() else ''
                )

                kwargs = {
                    "content": content,
                    "bot": self.bot,
                    "match": match,
                    "value": value,
                    "author": message.author,
                    **groups,
                }

                try:
                    formatted_msg = joke["message"].format(**kwargs)
                except (KeyError, IndexError):
                    formatted_msg = joke["message"].format(
                        content=content, bot=self.bot, match=match
                    )

                await message.reply(formatted_msg, mention_author=False)
                break


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Dad(bot))
