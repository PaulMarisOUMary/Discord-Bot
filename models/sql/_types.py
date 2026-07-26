from typing import Annotated, Any, TypeAlias

from sqlalchemy.dialects.mysql import BIGINT, MEDIUMINT, SMALLINT
from sqlmodel import Field


class Unsigned:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("unsigned", True)
        super().__init__(*args, **kwargs)

class BigIntUnsigned(Unsigned, BIGINT): ...


class SmallIntUnsigned(Unsigned, SMALLINT): ...


class MediumIntUnsigned(Unsigned, MEDIUMINT): ...


SnowflakePK: TypeAlias = Annotated[
    int,
    Field(primary_key=True, sa_type=BigIntUnsigned, sa_column_kwargs={"autoincrement": False}),
]

Snowflake: TypeAlias = Annotated[int, Field(sa_type=BigIntUnsigned)]

UniqueSnowflake: TypeAlias = Annotated[int, Field(sa_type=BigIntUnsigned, unique=True)]

Counter16: TypeAlias = Annotated[int, Field(default=0, sa_type=SmallIntUnsigned)]
Counter24: TypeAlias = Annotated[int, Field(default=0, sa_type=MediumIntUnsigned)]