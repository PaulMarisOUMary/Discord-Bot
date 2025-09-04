import discord

from discord.ext import commands, tasks
from typing import Dict

from utils.basebot import DiscordBot


class Presence(commands.Cog, name="presence"):
    """A loop to set the current presence of the bot."""
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig_data = self.bot.config["cogs"][self.__cog_name__.lower()]

        self.count = 0

        self.status_match: Dict[str, discord.Status] = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible,
            "offline": discord.Status.offline
        }

    async def cog_load(self) -> None:
        self.task_change_status.change_interval(seconds=self.subconfig_data["cooldown"])
        self.task_change_status.start()

    async def cog_unload(self) -> None:
        self.task_change_status.cancel()

    @tasks.loop()
    async def task_change_status(self) -> None:
        await self.bot.wait_until_ready()
        
        next = self.subconfig_data["status"][self.count]
        status = self.status_match[next.get("status", "online").lower()]
        name = next.get("name", None)

        await self.bot.change_presence(
            activity=discord.CustomActivity(name), 
            status=status
        )

        self.count = (self.count + 1) % len(self.subconfig_data["status"])


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Presence(bot))