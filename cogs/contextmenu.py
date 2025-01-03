import discord

from classes.discordbot import DiscordBot
from classes.translator import Translator

from discord.ext import commands
from discord import app_commands

class ContextMenu(commands.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.context_commands = [
            app_commands.ContextMenu(
                name = "Translate in English",
                callback = self.translate_to_english,
                type = discord.AppCommandType.message,
            ),
            app_commands.ContextMenu(
                name = "Translate",
                callback = self.translate_to_your_language,
                type = discord.AppCommandType.message,
            )
        ]

        for command in self.context_commands:
            self.bot.tree.add_command(command)

    async def cog_unload(self) -> None:
        for command in self.context_commands:
            self.bot.tree.remove_command(str(command), type=command.type)

    async def translate(self, interaction: discord.Interaction, message: discord.Message, destination: str = "en") -> None:
        content = message.content

        analysis = await Translator.detect(content)
        flag_emoji = Translator.get_emoji(analysis)
        translation = await Translator.translate(message.content, dest=destination, src="auto")

        await interaction.response.send_message(f"{flag_emoji} -> {Translator.get_emoji(destination)} **:** {translation}", ephemeral=True)

    async def translate_to_english(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await self.translate(interaction, message, "en")

    async def translate_to_your_language(self, interaction: discord.Interaction, message: discord.Message) -> None:
        dest = Translator.get_trans_abbr(str(interaction.locale))
        await self.translate(interaction, message, dest)



async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(ContextMenu(bot))