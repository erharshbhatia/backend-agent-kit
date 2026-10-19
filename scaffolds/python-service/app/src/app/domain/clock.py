"""Injected time. Nothing else reads the wall clock (ruff banned-api enforces it)."""

from datetime import UTC, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Current time, timezone-aware UTC."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FrozenClock:
    """Test clock: returns a fixed instant until advanced."""

    def __init__(self, at: datetime) -> None:
        if at.tzinfo is None:
            raise ValueError("FrozenClock needs a timezone-aware datetime")
        self._at = at

    def now(self) -> datetime:
        return self._at

    def advance(self, by: timedelta) -> None:
        self._at += by
