"""Readiness: is this process able to serve? Used by `/readyz` and container health checks."""

from dataclasses import dataclass

from app.persistence.ports.database import Database


@dataclass(frozen=True, slots=True)
class Readiness:
    ready: bool
    checks: dict[str, str]


async def check_readiness(database: Database) -> Readiness:
    """Ping each dependency. Never raises: a failed dependency is reported, not thrown."""
    try:
        await database.ping()
    # Any failure means "not ready"; it is reported, not swallowed.
    except Exception as error:
        return Readiness(ready=False, checks={"database": f"failed: {type(error).__name__}"})
    return Readiness(ready=True, checks={"database": "ok"})
