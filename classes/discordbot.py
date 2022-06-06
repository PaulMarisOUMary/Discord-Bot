from discord.ext import commands
from logging import Logger
from typing import Any

from classes.database import DataSQL

class DiscordBot(commands.Bot):
    """A Subclass of `commands.Bot`."""

    config: dict
    """The config loaded directly from 'config/*.json'."""

    database: DataSQL
    """Represent the database connection."""

    logger: Logger
    """Logging Object of the bot."""

    prefixes: dict
    """List of prefixes per guild."""

    def __init__(self,**kwargs: Any) -> None:
        super().__init__(**kwargs)