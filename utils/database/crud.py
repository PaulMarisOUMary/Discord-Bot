from collections.abc import Iterable
from typing import Any, TypeVar

from sqlalchemy import Table, func, inspect
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


def get_table(model: type[ModelType]) -> Table:
    mapper = inspect(model)
    if mapper is None:
        raise TypeError(f"{model!r} is not a mapped SQLModel table")

    return mapper.local_table


async def upsert(
    session: AsyncSession, obj: ModelType, *, exclude: Iterable[str] = ()
) -> None:
    table = get_table(type(obj))
    pk_columns = {column.name for column in table.primary_key.columns}
    skip = pk_columns | set(exclude)

    values = obj.model_dump()
    update = {key: value for key, value in values.items() if key not in skip}

    statement = mysql_insert(table).values(**values)
    if update:
        statement = statement.on_duplicate_key_update(**update)

    await session.exec(statement)


async def increment(
    session: AsyncSession,
    model: type[ModelType],
    keys: dict[str, Any],
    target: str,
    *,
    amount: int = 1,
) -> None:
    table = get_table(model)
    column = table.c[target]

    statement = mysql_insert(table).values(**keys, **{target: amount})
    statement = statement.on_duplicate_key_update(
        **{target: func.coalesce(column, 0) + amount}
    )

    await session.exec(statement)
