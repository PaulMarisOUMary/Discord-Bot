import discord
import re

from classes.translator import Translator

from discord.ext import commands
from discord import app_commands

class ContextMenu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.context_commands: list[app_commands.ContextMenu] = [
            app_commands.ContextMenu(
                name = "Join Date",
                callback = self.join_date,
                type = discord.AppCommandType.user,
                #guild_ids=[id, id, ...]
            ),
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

    async def cog_unload(self):
        for command in self.context_commands:
            self.bot.tree.remove_command(command, command.type)

    async def join_date(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"{member.mention} joined the {discord.utils.format_dt(member.joined_at)}", ephemeral=True)

    async def translate(self, interaction: discord.Interaction, message: discord.Message, destination: str = "en"):
        content = message.content

        mention_regex = re.compile(r"<[@|@& ]*&*[0-9]+>") 	#@
        channel_regex = re.compile(r"<# [0-9]+>")			##
        emote_regex = re.compile(r"<: \w+: [0-9]+>") 		#::

        analysis = Translator.detect(content)
        flag_emoji = Translator.get_emoji(analysis)
        translation = Translator.translate(message.content, dest=destination, src="auto")

        for regex in [mention_regex, channel_regex, emote_regex]:
            targets = regex.findall(translation)
            for target in targets:
                translation = translation.replace(target, target.replace(' ', ''))

        await interaction.response.send_message(f"{flag_emoji} -> {Translator.get_emoji(destination)} **:** {translation}", ephemeral=True)

    async def translate_to_english(self, interaction: discord.Interaction, message: discord.Message):
        await self.translate(interaction, message, "en")

    async def translate_to_your_language(self, interaction: discord.Interaction, message: discord.Message):
        dest = Translator.get_trans_abbr(str(interaction.locale))
        await self.translate(interaction, message, dest)

async def setup(bot):
    await bot.add_cog(ContextMenu(bot))