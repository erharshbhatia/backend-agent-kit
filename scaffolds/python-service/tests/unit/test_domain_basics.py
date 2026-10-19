"""Injected time and ids behave deterministically in tests."""

import asyncio
from datetime import timedelta

from app.domain.clock import FrozenClock
from app.domain.ids import SeededIdGenerator, UuidV7Generator
from app.entrypoints.worker import run_worker


def test_frozen_clock_moves_only_when_advanced(frozen_clock: FrozenClock) -> None:
    start = frozen_clock.now()
    assert frozen_clock.now() == start
    frozen_clock.advance(timedelta(seconds=5))
    assert frozen_clock.now() - start == timedelta(seconds=5)


def test_seeded_ids_repeat_for_the_same_seed_and_are_ordered() -> None:
    assert SeededIdGenerator(seed=7).new() == SeededIdGenerator(seed=7).new()
    ids = SeededIdGenerator(seed=7)
    a, b = ids.new(), ids.new()
    assert a.version == 7
    assert a < b


def test_production_ids_are_uuid_v7() -> None:
    assert UuidV7Generator().new().version == 7


async def test_worker_keeps_running_after_a_failing_tick() -> None:
    stop = asyncio.Event()
    calls = 0

    async def tick() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("boom")
        if calls == 3:
            stop.set()

    ticks = await run_worker(tick=tick, poll_interval_s=0.001, stop=stop)
    assert ticks == 3
