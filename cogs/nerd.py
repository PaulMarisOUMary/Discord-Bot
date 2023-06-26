import discord

from discord.ext import commands

from classes.discordbot import DiscordBot

class Nerd(commands.Cog, name="nerd"):
    """
        He do be deserving it tho.

        Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

        self.target = self.subconfig_data["id"]
        self.EMOJI = self.subconfig_data["react"]

    def help_custom(self) -> tuple[str, str, str]:
        emoji = self.EMOJI
        label = "Nerd"
        description = "For when someone is being a nerd."
        return emoji, label, description

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message: discord.Message) -> None:
        if message.author.id == self.target:
            await message.add_reaction(self.EMOJI)