from msgspec import Struct


class PrefixConfig(Struct):
    default: str
    mentionable: bool


class BotConfig(Struct):
    prefix: PrefixConfig
    use_database: bool