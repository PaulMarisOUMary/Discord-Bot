from asyncio import BaseTransport, Protocol, Transport
from logging import getLogger
from typing import cast

from discord.ext import commands

from utils.bot import DiscordBot
from utils.cogs import cogs_manager, get_cogs
from utils.config import load_config
from utils.paths import cogs_dir, config_dir, env_path

_log = getLogger(__name__)


class ServerProtocol(Protocol):
    def __init__(self, bot: DiscordBot) -> None:
        super().__init__()
        self.bot = bot

    async def process_message(self, message: str) -> None:
        match message:
            case "ping":
                _log.info(f"{self.str_conn} Ping received")
            case "reload":
                self.bot.config = load_config(config_dir, env_path)

                await cogs_manager(
                    self.bot, "unload", *[cog for cog in self.bot.extensions]
                )

                await cogs_manager(
                    self.bot, "load", *get_cogs(cogs_dir, self.bot.config.cogs.disabled)
                )

                await self.bot.tree.sync()
            case _:
                _log.warning(f"{self.str_conn} Unknown message received: {message}")

    def connection_made(self, transport: BaseTransport) -> None:
        self.host, self.port = transport.get_extra_info("peername")
        self.str_conn = f"({self.host}:{self.port}) :"

        _log.debug(f"{self.str_conn} Connection made")
        self.transport = cast(Transport, transport)

    def data_received(self, data) -> None:
        message = data.decode(encoding="utf-8")
        _log.info(f"{self.str_conn} Data received: {message}")

        self.bot.loop.create_task(self.process_message(message))

        self.transport.write(data)
        _log.debug(f"{self.str_conn} Answered")

        self.transport.close()
        _log.debug(f"{self.str_conn} Connection closed")


class SocketTransport(commands.Cog, name="socket"):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    async def startup_server(self) -> None:
        self.server = await self.bot.loop.create_server(
            protocol_factory=lambda: ServerProtocol(self.bot),
            host="127.0.0.1",
            port=50000,
        )

        async with self.server:
            await self.server.serve_forever()

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self.startup_server())
        _log.debug("Socket server started")

    async def cog_unload(self) -> None:
        self.server.close()
        _log.debug("Socket server stopped")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(SocketTransport(bot))
