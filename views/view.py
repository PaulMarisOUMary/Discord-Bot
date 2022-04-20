import discord

class View(discord.ui.View):
    """Parent class dedicated to Views"""
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: any):
        interaction.client.dispatch("view_error", interaction, error, item)