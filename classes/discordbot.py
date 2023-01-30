from datetime import datetime
from discord import __version__ as discord_version
from discord import AppInfo, Message
from discord.ext import commands
from logging import Logger
from logging import INFO as LOG_INFO
from typing import List, Self

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

    prefixes: dict = dict()
    """List of prefixes per guild."""

    uptime: datetime = datetime.now()
    """Bot's uptime."""
    
    usedatabase: bool = True
    """Whether the bot should use the database or not."""

    def __init__(self,**kwargs):
        """Initialize the bot.
        
        Parameters
        ----------
        config : dict
            By default: The configuration loaded from 'config/*.json'.
        intents : discord.Intents
            Used to enable/disable certain gateway features used by your bot.
        
        The `command_prefix` kwarg is unused, this attribute is automatically set according to the database configuration (use_database).
        """
        self.config = kwargs.pop("config", None)
        
        if not self.config or not all(item in self.config.keys() for item in ["bot", "database"]): # cogs.json is an optional configuration file
            raise ValueError("Missing required configuration.")
        
        self.usedatabase = self.config["database"]["use_database"]
        
        kwargs.pop("command_prefix", None) # remove kwarg if exists
        command_prefix = self.__prefix_callable if self.usedatabase else self.config["bot"]["default_prefix"]
        
        super().__init__(command_prefix = command_prefix, **kwargs)

    def log(self, message: str, name: str, level: int = LOG_INFO, **kwargs):
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
        
    def __prefix_callable(self, client: Self, message: Message) -> List[str]:
        if message.guild is None:
            return commands.when_mentioned_or(self.config["bot"]["default_prefix"])(client, message)

        if (guild_id := message.guild.id) in client.prefixes: 
            prefix = client.prefixes[guild_id]
        else: 
            prefix = self.config["bot"]["default_prefix"]
        return commands.when_mentioned_or(prefix)(client, message)

    async def on_ready(self):
        self.log( message = f"Logged as: {self.user} | discord.py{discord_version} Guilds: {len(self.guilds)} Users: {len(self.users)} Config: {len(self.config)} Database: {self.usedatabase}", name = "discord.on_ready")

    async def setup_hook(self):
        # Retrieve the bot's application info
        self.appinfo = await self.application_info()

        if self.usedatabase:
            # Database initialization
            server = self.config["database"]["server"]
            self.database = DataSQL(server["host"], server["port"], self.loop)
            await self.database.auth(server["user"], server["password"], server["database"])
            self.log(message = f"Database connection established ({server['host']}:{server['port']})", name = "discord.setup_hook")

            # Prefix per guild initialization
            for data in await self.database.select(self.config["bot"]["prefix_table"]["table"], "*"): 
                self.prefixes[data[0]] = data[1]

    async def close(self):
        if self.usedatabase:
            await self.database.close()
            self.log(message = "Database connection closed", name = "discord.close")

        await super().close()