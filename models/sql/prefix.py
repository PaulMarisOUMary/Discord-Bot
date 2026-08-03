from sqlmodel import Field, SQLModel

from ._types import SnowflakePK


class Prefix(SQLModel, table=True):
    __tablename__ = "table_prefix"

    guild_id: SnowflakePK
    guild_prefix: str | None = Field(default=None, max_length=256)