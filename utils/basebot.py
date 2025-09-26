from __future__ import annotations

from datetime import datetime
from logging import INFO, Logger
from typing import Any, Dict, List
from discord import __version__ as discord_version, AppInfo, Message
from discord.ext import commands

from utils.database import DataSQL
from utils.helper import cogs_manager, get_cogs


class DiscordBot(commands.Bot):
    appinfo: AppInfo

    config: Dict[Any, Any]
    database: DataSQL

    logger: Logger

    prefixes: Dict[int, str] = dict()

    uptime: datetime = datetime.now()

    use_database: bool = True

    def __init__(self, **kwargs: Any) -> None:
        self.config = kwargs.pop("config", dict())
        self.config["env"] = kwargs.pop("env", dict())

        self.use_database = self.config["bot"]["use_database"]

        self.__prefix_default = self.config["bot"]["prefix"]["default"]

        kwargs.pop("command_prefix", None)
        super().__init__(command_prefix=self.__prefix_callable, **kwargs)

    def __prefix_callable(self: DiscordBot, client: DiscordBot, message: Message) -> List[str]:
        if message.guild is None or not self.use_database:
            return commands.when_mentioned_or(self.__prefix_default)(client, message)

        if (guild_id := message.guild.id) in client.prefixes: 
            prefix = client.prefixes[guild_id]
        else: 
            prefix = self.__prefix_default
        return commands.when_mentioned_or(prefix)(client, message)
    
    def log(self, message: str, name: str, level: int = INFO, **kwargs) -> None:
        self.logger.name = name
        self.logger.log(level, message, **kwargs)

    async def on_ready(self) -> None:
        self.log(f"Logged in as {self.user} (UID: {self.appinfo.id}) | discord.py{discord_version} | Guilds: {len(self.guilds)} Users: {len(self.users)} Config: {len(self.config)} Database: {self.use_database}", "discord.on_ready")

    async def startup(self) -> None:
        await self.wait_until_ready()

        synced = await self.tree.sync()
        self.log(message = f"Application commands synced ({len(synced)})", name = "discord.startup")

    async def setup_hook(self) -> None:
        if self.use_database:
            env = self.config["env"]
            host = env["MARIADB_HOST"]
            user = env["MARIADB_USER"]
            password = env["MARIADB_PASSWORD"]
            database = env["MARIADB_DATABASE"]

            self.database = DataSQL(host=host, loop=self.loop)
            try:
                await self.database.auth(user=user, password=password, database=database)
                self.log(message = f"Database connection established ({host}:{database})", name = "discord.setup_hook")

                for data in await self.database.select(self.config["bot"]["prefix"]["table"], '*'):
                    self.prefixes[data[0]] = data[1]
            except Exception as e:
                raise ConnectionError(f"Database connection failed on {host} for user {user}.") from e
        
        self.appinfo = await self.application_info()

        cogs = get_cogs("cogs")
        await cogs_manager(self, "load", cogs)
        self.log(message = f"Cogs loaded ({len(cogs)}): {', '.join(cogs)}", name = "discord.setup_hook")

        self.loop.create_task(self.startup())

    async def close(self) -> None:
        if self.use_database:
            await self.database.close()
            self.log(message = "Database connection closed", name = "discord.close")

        await super().close()