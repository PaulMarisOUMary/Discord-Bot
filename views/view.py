import discord

from typing import Any

class View(discord.ui.View):
    """Parent class dedicated to Views"""
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: Any) -> None:
        interaction.client.dispatch("view_error", interaction, error, item)