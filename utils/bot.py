from __future__ import annotations

from logging import Logger, getLogger
from time import monotonic
from typing import Any

from discord import AppInfo, Message
from discord import __version__ as d_version
from discord.ext import commands
from sqlmodel import select

from models.config import Config
from utils.cogs import cogs_manager, get_cogs
from utils.database import Database
from utils.paths import root_dir

_log = getLogger(__name__)

class DiscordBot(commands.Bot):
    appinfo: AppInfo
    config: Config
    database: Database | None
    logger: Logger
    prefixes_cache: dict[int, str]

    @property
    def uptime(self) -> float:
        return monotonic() - self._start_time

    def __init__(self, config: Config, **kwargs: Any) -> None:
        self._start_time = monotonic()

        self.config = config

        self.prefixes_cache = {}
        self._prefix_default = self.config.bot.prefix.default

        super().__init__(command_prefix=self._get_prefix, **kwargs)

    def _get_prefix(self, client: DiscordBot, message: Message) -> list[str]:
        if message.guild is None or not self.config.bot.use_database:
            prefix = self._prefix_default
        else:
            prefix = self.prefixes_cache.get(message.guild.id, self._prefix_default)

        if self.config.bot.prefix.mentionable:
            return commands.when_mentioned_or(prefix)(client, message)

        return [prefix]

    async def on_ready(self) -> None:
        _log.info(f"Logged in as {self.user} (UID: {self.appinfo.id}) | discord.py{d_version} | Guilds: {len(self.guilds)} Users: {len(self.users)}")

    async def startup(self) -> None:
        await self.wait_until_ready()

        synced = await self.tree.sync()
        _log.info(f"Application commands synced ({len(synced)}).")

    async def setup_hook(self) -> None:
        self.database = None

        if self.config.bot.use_database:
            from models.sql import Prefix

            env = self.config.env
            self.database = Database(env.mariadb_host)
            await self.database.connect(
                user=env.mariadb_user,
                password=env.mariadb_password,
                database=env.mariadb_database,
            )
            await self.database.init_models()

            async with self.database.session() as session:
                prefixes = (await session.exec(select(Prefix))).all()
                self.prefixes_cache = {
                    prefix.guild_id: prefix.guild_prefix
                    for prefix in prefixes
                    if prefix.guild_prefix
                }

            _log.info("Database connected and models initialized.")

        self.appinfo = await self.application_info()

        cogs = get_cogs(root_dir / "cogs", self.config.cogs.disabled)
        await cogs_manager(self, "load", *cogs)

        self.loop.create_task(self.startup())

    async def close(self) -> None:
        if self.config.bot.use_database and self.database is not None:
            await self.database.close()
            _log.info("Database connection closed.")

        await super().close()