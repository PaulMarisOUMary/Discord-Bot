from sqlmodel import Field, SQLModel

from ._types import SnowflakePK


class Me(SQLModel, table=True):
    __tablename__ = "table_me"

    guild_id: SnowflakePK
    user_id: SnowflakePK

    user_me: str | None = Field(default=None, max_length=1024)