import discord

from utils.basebot import DiscordBot
from utils.translator import Translator

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

    async def translate(self, interaction: discord.Interaction, message: discord.Message, locale: discord.Locale) -> None:
        content = message.content.strip()

        if not content:
            await interaction.response.send_message("The message is empty.", ephemeral=True)
            return

        analysis = await Translator.detect(content)
        flag_emoji = Translator.code_to_flag(analysis)
        translation = await Translator.translate_to_locale(message.content, locale)

        await interaction.response.send_message(f"{flag_emoji} -> {Translator.locale_to_flag(locale)} **:** {translation}", ephemeral=True)

    async def translate_to_english(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await self.translate(interaction, message, discord.Locale.british_english)

    async def translate_to_your_language(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await self.translate(interaction, message, interaction.locale)



async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(ContextMenu(bot))