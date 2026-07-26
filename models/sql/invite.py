from sqlmodel import Field, SQLModel

from ._types import Snowflake, SnowflakePK


class Invite(SQLModel, table=True):
    __tablename__ = "table_invite"

    guild_id: SnowflakePK
    channel_id: Snowflake
    custom_message: str | None = Field(default=None, max_length=4096)