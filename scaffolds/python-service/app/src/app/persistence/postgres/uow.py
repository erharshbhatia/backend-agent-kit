"""PostgresUnitOfWork: one pooled connection and one transaction.

Repositories are attached as properties, one per port, e.g.:

    @property
    def orders(self) -> OrderRepository:
        return self._repository(PostgresOrderRepository)
"""

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine


class UnitOfWorkMisuse(RuntimeError):
    """A unit of work was used outside its `async with` block."""


class PostgresUnitOfWork:
    """Implements `UnitOfWork`. READ COMMITTED per transaction."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._connection: AsyncConnection | None = None

    async def __aenter__(self) -> Self:
        self._connection = await self._engine.connect()
        await self._connection.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        connection = self._require()
        try:
            if connection.in_transaction():
                await connection.rollback()
        finally:
            await connection.close()
            self._connection = None

    async def commit(self) -> None:
        connection = self._require()
        await connection.commit()
        await connection.begin()

    async def rollback(self) -> None:
        connection = self._require()
        await connection.rollback()
        await connection.begin()

    def _require(self) -> AsyncConnection:
        if self._connection is None:
            raise UnitOfWorkMisuse("use the unit of work inside `async with`")
        return self._connection
