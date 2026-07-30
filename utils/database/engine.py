from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

_log = getLogger(__name__)


class Database:
    def __init__(self, host: str, port: int = 3306) -> None:
        self.host = host
        self.port = port

        self.engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def connect(
        self, user: str, password: str, database: str, *, echo: bool = False
    ) -> None:
        url = f"mysql+asyncmy://{user}:{password}@{self.host}:{self.port}/{database}"

        self.engine = create_async_engine(
            url,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        self._sessionmaker = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        _log.info(f"Connected to database '{database}' at {self.host}:{self.port}.")

    async def init_models(self) -> None:
        if self.engine is None:
            raise RuntimeError("Database.connect() must be called before init_models()")

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    def session(self) -> AsyncSession:
        if self._sessionmaker is None:
            raise RuntimeError("Database.connect() must be called before session()")

        return self._sessionmaker()

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            _log.info("Database connection closed.")
