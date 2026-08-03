from sqlmodel import Field, SQLModel

from ._types import Counter24


class Metric(SQLModel, table=True):
    __tablename__ = "table_metrics"

    command_name: str = Field(max_length=32, primary_key=True)
    command_type: str = Field(max_length=32, primary_key=True)

    command_count: Counter24