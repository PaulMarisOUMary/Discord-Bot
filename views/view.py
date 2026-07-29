from typing import Any

from discord import Interaction
from discord.ui import Item
from discord.ui import View as dView


class View(dView):
    """Parent class dedicated to Views"""

    async def on_error(
        self, interaction: Interaction, error: Exception, item: Item[Any]
    ) -> None:
        interaction.client.dispatch("view_error", interaction, error, item)
