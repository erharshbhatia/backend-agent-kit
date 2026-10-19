"""Injected ids (UUIDv7: time-ordered, index-friendly). Nothing else generates ids inline."""

import os
import random
import time
from typing import Protocol
from uuid import UUID


class IdGenerator(Protocol):
    def new(self) -> UUID:
        """A new unique id."""
        ...


def _uuid7(unix_ms: int, rand: bytes) -> UUID:
    # RFC 9562: 48-bit ms timestamp | version 7 | 12 random bits | variant 0b10 | 62 random bits.
    rand_a = int.from_bytes(rand[:2], "big") & 0x0FFF
    rand_b = int.from_bytes(rand[2:10], "big") & ((1 << 62) - 1)
    value = (unix_ms & ((1 << 48) - 1)) << 80 | 0x7 << 76 | rand_a << 64 | 0b10 << 62 | rand_b
    return UUID(int=value)


class UuidV7Generator:
    """Production ids from the wall clock and the OS random source."""

    def new(self) -> UUID:
        return _uuid7(time.time_ns() // 1_000_000, os.urandom(10))


class SeededIdGenerator:
    """Test ids: deterministic for a given seed and start time."""

    def __init__(self, seed: int, *, start_ms: int = 1_767_225_600_000) -> None:
        self._random = random.Random(seed)
        self._ms = start_ms

    def new(self) -> UUID:
        self._ms += 1
        return _uuid7(self._ms, self._random.randbytes(10))
