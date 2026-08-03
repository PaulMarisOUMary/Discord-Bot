from datetime import date

from sqlmodel import SQLModel

from ._types import SnowflakePK


class Birthday(SQLModel, table=True):
    __tablename__ = "table_birthday"

    guild_id: SnowflakePK
    user_id: SnowflakePK

    user_birth: date