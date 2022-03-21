import discord
import re

from discord.ext import commands
from random import random

class Dad(commands.Cog, name="dad", command_attrs=dict(hidden=True)):
    """Dad's jokes."""
    def __init__(self, bot) -> None:
        self.bot = bot
        self.settings = bot.bot_data["dad"]
        self.pattern = re.compile(r"""
                                    ^(.*?[\s])?         # Some text
                                    (im|i\ am|i\'m)[\s] # The "i'm" and a whitespace
                                    (?P<name>.+)        # The name
                                    """, re.VERBOSE + re.IGNORECASE)

    def help_custom(self) -> tuple[str]:
        emoji = '👨‍🦳'
        label = "Dad's jokes"
        description = "Ahah, it was a good one!"
        return emoji, label, description

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message : discord.Message):
        author_id = message.author.id
        if author_id != self.bot.user.id:
            content = message.content
            channel = message.channel

            im = self.pattern.search(content)
            if im and random() <= self.settings["probability"]:
                name = im.group("name").strip()
                id_ = re.search("<@!?(?P<id>\d{17,19})>", name) # https://github.com/discordjs/discord.js/blob/2f6f365098cbab397cda124711c4bb08da850a17/src/structures/MessageMentions.js#L221
                if id_ and int(id_.group("id")) != author_id:
                    await channel.send(f"No you are {message.author.mention}")
                else:
                    await channel.send(f"Hi {name}, I'm {self.bot.user.mention}")

def setup(bot):
    bot.add_cog(Dad(bot))
