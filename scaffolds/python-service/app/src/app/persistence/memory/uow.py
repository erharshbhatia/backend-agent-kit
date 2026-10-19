"""MemoryUnitOfWork and MemoryDatabase: the test twins of the Postgres implementations.

Repositories stage writes on the unit of work and apply them on `commit()`, so rollback
semantics match Postgres. The shared contract suite runs against both.
"""

from types import TracebackType
from typing import Self


class MemoryDatabase:
    """`Database` port that is always reachable (or never, for readiness tests)."""

    def __init__(self, *, reachable: bool = True) -> None:
        self.reachable = reachable
        self.closed = False

    async def ping(self) -> None:
        if not self.reachable:
            raise ConnectionError("memory database marked unreachable")

    async def close(self) -> None:
        self.closed = True


class MemoryUnitOfWork:
    """Implements `UnitOfWork` over in-process state."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.rollback()

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1
