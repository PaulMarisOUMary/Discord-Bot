import typing
import discord

from discord.ext import commands
from discord import app_commands

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Display the avatar.")
    @app_commands.guilds(discord.Object(id=332234497078853644))
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        if not user:
            user = interaction.user
        await interaction.response.send_message(user.display_avatar.url)



async def setup(bot):
    await bot.add_cog(Slash(bot))