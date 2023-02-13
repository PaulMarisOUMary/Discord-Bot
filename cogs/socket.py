import asyncio

from classes.discordbot import DiscordBot

from discord.ext import commands


class ServerProtocol(asyncio.Protocol):
    def __init__(self, bot: DiscordBot):
        super().__init__()
        self.bot = bot

    def process_message(self, message: str):
        raise NotImplementedError()

    def connection_made(self, transport: asyncio.Transport):
        self.host, self.port = transport.get_extra_info("peername")
        self.str_conn = f"({self.host}:{self.port}) :"

        self.bot.log(f"{self.str_conn} Connection made", "discord.socket")
        self.transport = transport

    def data_received(self, data):
        message = data.decode(encoding="utf-8")
        self.bot.log(f"{self.str_conn} Data received: {message}", "discord.socket")
        
        self.process_message(message)

        self.transport.write(data)
        self.bot.log(f"{self.str_conn} Answered", "discord.socket")

        self.transport.close()
        self.bot.log(f"{self.str_conn} Connection closed", "discord.socket")


class SocketTransport(commands.Cog, name="socket"):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    async def startup_server(self):
        self.server = await self.bot.loop.create_server(
            protocol_factory = lambda: ServerProtocol(self.bot),
            host = "127.0.0.1",
            port = 50000
        )

        async with self.server:
            await self.server.serve_forever()

    async def cog_load(self):
        self.bot.loop.create_task(self.startup_server())
        self.bot.log("Socket server started", "discord.socket")

    async def cog_unload(self):
        self.server.close()
        self.bot.log("Socket server stopped", "discord.socket")


async def setup(bot: DiscordBot):
    await bot.add_cog(SocketTransport(bot))
