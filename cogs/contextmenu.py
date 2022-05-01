import discord

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
                name = "Translate to English",
                callback = self.translate,
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

    async def translate(self, interaction: discord.Interaction, message: discord.Message):
        content = message.content

        analysis = Translator.detect(content)
        flag_emoji = Translator.get_emoji(analysis)
        translation = Translator.translate(message.content, dest="en", src="auto")
        await interaction.response.send_message(f"{flag_emoji} -> {Translator.get_emoji('en')} **:** {translation}", ephemeral=True)

async def setup(bot):
	await bot.add_cog(ContextMenu(bot))