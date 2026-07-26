from typing import Any

from msgspec import Struct

from .bot import BotConfig
from .cogs import CogsConfig
from .env import EnvConfig


class Config(Struct):
    bot: BotConfig
    cogs: CogsConfig
    env: EnvConfig


__all__ = [
    "BotConfig",
    "CogsConfig",
    "Config",
    "EnvConfig",
]