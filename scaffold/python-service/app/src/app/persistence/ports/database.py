"""The database as a dependency: reachable or not, and closable."""

from typing import Protocol


class Database(Protocol):
    async def ping(self) -> None:
        """Round-trip to the database. Raises if it is unreachable."""
        ...

    async def close(self) -> None:
        """Release pooled connections."""
        ...
