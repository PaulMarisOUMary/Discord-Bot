from msgspec import Struct


class EnvConfig(Struct):
    bot_token: str
    mariadb_database: str
    mariadb_host: str
    mariadb_user: str
    mariadb_password: str