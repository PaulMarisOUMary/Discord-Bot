from sqlmodel import SQLModel

from ._types import Counter16, Snowflake, SnowflakePK, UniqueSnowflake


class Starboard(SQLModel, table=True):
    __tablename__ = "table_starboard"

    reference_message_id: SnowflakePK
    reference_guild_id: Snowflake
    reference_channel_id: Snowflake

    display_channel_id: Snowflake
    display_message_id: UniqueSnowflake

    star_count: Counter16