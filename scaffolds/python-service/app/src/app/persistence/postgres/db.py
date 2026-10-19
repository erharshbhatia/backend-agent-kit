"""Async SQLAlchemy engine over psycopg 3 with a bounded connection pool."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.settings import DatabaseSettings


def create_engine(settings: DatabaseSettings) -> AsyncEngine:
    """Build the pooled async engine. No connection is opened until first use."""
    return create_async_engine(
        settings.url,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout_s,
        pool_recycle=settings.pool_recycle_s,
        echo=settings.echo_sql,
        connect_args={
            "connect_timeout": settings.connect_timeout_s,
            # Every statement is bounded: a stuck query fails instead of hanging.
            "options": f"-c statement_timeout={settings.statement_timeout_ms}",
        },
    )


class PostgresDatabase:
    """The `Database` port over an `AsyncEngine`."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def ping(self) -> None:
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def close(self) -> None:
        await self._engine.dispose()
