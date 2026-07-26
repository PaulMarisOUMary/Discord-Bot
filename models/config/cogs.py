from typing import Any

from msgspec import Struct


class GlobalConfig(Struct):
    disabled: list[str]


class CogsConfig(GlobalConfig):
    cogs: dict[str, dict[str, Any]]