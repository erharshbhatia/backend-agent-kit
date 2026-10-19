"""Typed results repository ports return instead of raising (repository.md, R9 and R10)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Created[T]:
    """The row was inserted by this call."""

    value: T


@dataclass(frozen=True, slots=True)
class Existing[T]:
    """A row with the same idempotency key was already stored; `value` is that row."""

    value: T


type InsertResult[T] = Created[T] | Existing[T]
"""What an idempotent `add` returns: the caller matches on the variant, never on an exception."""


@dataclass(frozen=True, slots=True)
class Page[T]:
    """One page of a keyset-paginated list. `next_cursor` is None on the last page."""

    items: tuple[T, ...]
    next_cursor: str | None
