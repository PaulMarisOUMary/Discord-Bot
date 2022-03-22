import discord

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from typing import List

class Slash(commands.Cog):
    """Slash commands example."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fruits_autocomplete(self, _: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
        return [
            app_commands.Choice(name=fruit, value=fruit)
            for fruit in fruits if current.lower() in fruit.lower()
        ]
    @app_commands.command(name="fruits", description="Fruit suggestion.")
    @app_commands.guilds(discord.Object(id=332234497078853644))
    @app_commands.autocomplete(fruits=fruits_autocomplete)
    async def fruits(self, interaction: discord.Interaction, fruits: str):
        await interaction.response.send_message(f'Your favourite fruit seems to be {fruits}')

    @app_commands.command(name="fruit", description="Fruit choice.")
    @app_commands.describe(fruits='fruits to choose from')
    @app_commands.choices(fruits=[
        Choice(name='apple', value=1),
        Choice(name='banana', value=2),
        Choice(name='cherry', value=3),
        ]
    )
    @app_commands.guilds(discord.Object(id=332234497078853644))
    async def fruit(self, interaction: discord.Interaction, fruits: Choice[int]):
        await interaction.response.send_message(f'Your favourite fruit is {fruits.name}.')

    @app_commands.command(name="avatar", description="Display the avatar.")
    @app_commands.describe(user="The user to get the avatar from.")
    @app_commands.guilds(discord.Object(id=332234497078853644))
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        if not user:
            user = interaction.user
        await interaction.response.send_message(user.display_avatar.url)



async def setup(bot):
    await bot.add_cog(Slash(bot))