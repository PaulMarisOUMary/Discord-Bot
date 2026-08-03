from sqlmodel import SQLModel

from ._types import Counter16, SnowflakePK


class Croissant(SQLModel, table=True):
    __tablename__ = "table_croissants"

    user_id: SnowflakePK
    user_count: Counter16