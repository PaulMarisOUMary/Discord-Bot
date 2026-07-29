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
