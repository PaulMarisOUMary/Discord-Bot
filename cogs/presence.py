from typing import Any

from discord import CustomActivity, Status
from discord.ext import commands, tasks

from utils.bot import DiscordBot

STATUS_MATCH = {
    "online": Status.online,
    "idle": Status.idle,
    "dnd": Status.dnd,
    "invisible": Status.invisible,
    "offline": Status.offline,
}


class Presence(commands.Cog, name="presence"):
    """A loop to set the current presence of the bot."""

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.count = 0

    async def cog_load(self) -> None:
        raw_cooldown = self.subconfig.get("cooldown", 30)
        cooldown = max(12, raw_cooldown)

        self.task_change_status.change_interval(seconds=cooldown)
        self.task_change_status.start()

    async def cog_unload(self) -> None:
        self.task_change_status.cancel()

    @tasks.loop()
    async def task_change_status(self) -> None:
        statuses = self.subconfig.get("status", [])
        if not statuses:
            return

        current = statuses[self.count % len(statuses)]

        raw_status = str(current.get("status", "online")).lower()
        status = STATUS_MATCH.get(raw_status, Status.online)

        name = current.get("name")
        activity = CustomActivity(name) if name else None

        await self.bot.change_presence(
            activity=activity,
            status=status,
        )

        self.count = (self.count + 1) % len(statuses)

    @task_change_status.before_loop
    async def before_change_status(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Presence(bot))
