from logging import getLogger
from pathlib import Path
from typing import Literal

from discord.ext import commands

from utils.paths import root_dir

_log = getLogger(__name__)


def cog_to_path(cog: str) -> Path:
    return root_dir / f"{cog.replace('.', '/')}.py"

def sort_cogs(cogs: list[str], reverse: bool = False) -> list[str]:
    def sortlatest(cog: str) -> tuple[float, str]:
        try:
            return (cog_to_path(cog).stat().st_mtime, cog)
        except OSError:
            return (0.0, cog)

    return sorted(cogs, key=sortlatest, reverse=reverse)

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

    _log.info(f"{action.capitalize()} {', '.join(cogs)}")

    for cog in cogs:
        await action_func(cog)