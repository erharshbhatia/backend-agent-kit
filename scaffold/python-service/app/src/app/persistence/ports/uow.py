"""Unit of work: one transaction exposing every repository.

Each phase adds one attribute per repository it introduces (e.g. `orders: OrderRepository`)
and implements it in the Postgres and memory units of work, with one shared contract suite.
"""

from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self


class UnitOfWork(Protocol):
    """One transaction. Nothing is visible to other units of work until `commit()`.

    Guarantees (checked by the contract suite on both implementations):
    - leaving the `async with` block without `commit()` rolls back, including on exceptions;
    - repositories never commit; only the unit of work does.
    """

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None:
        """Make all changes since the last commit durable and visible."""
        ...

    async def rollback(self) -> None:
        """Discard all changes since the last commit."""
        ...


UnitOfWorkFactory = Callable[[], UnitOfWork]
