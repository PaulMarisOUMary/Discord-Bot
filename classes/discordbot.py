from datetime import datetime
from discord import AppInfo
from discord.ext import commands
from logging import Logger
from logging import INFO as LOG_INFO

from classes.database import DataSQL

class DiscordBot(commands.Bot):
    """A Subclass of `commands.Bot`."""

    appinfo: AppInfo
    """Application info for the bot provided by Discord."""

    config: dict
    """The config loaded directly from 'config/*.json'."""

    database: DataSQL
    """Represent the database connection."""

    logger: Logger
    """Logging Object of the bot."""

    prefixes: dict
    """List of prefixes per guild."""

    uptime: datetime = datetime.now()
    """Bot's uptime."""

    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)

    def log(self, message: str, name: str, level: int = LOG_INFO, **kwargs) -> None:
        """Log a message to the console and the log file.

        Parameters
        ----------
        message : str
            The message to log.
        name : str
            The name of the logger.
        level : int
            The level of the log message.
        """
        self.logger.name = name
        self.logger.log(level = level, msg = message, **kwargs)