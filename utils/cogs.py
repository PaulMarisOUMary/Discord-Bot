from pathlib import Path
from typing import Literal

from discord.ext import commands


def get_cogs(cogs_dir: Path, disabled: list[str]) -> list[str]:
    cogs = []

    for file in cogs_dir.glob("*.py"):
        name = file.stem

        if name.startswith('_'):
            continue

        if name not in disabled:
            cogs.append(f"cogs.{name}")

    return cogs

async def cogs_manager(bot: commands.Bot, action: Literal["load", "unload", "reload"], *cogs: str) -> None:
    actions = {
        "load": bot.load_extension,
        "unload": bot.unload_extension,
        "reload": bot.reload_extension,
    }

    action_func = actions[action]

    for cog in cogs:
        await action_func(cog)