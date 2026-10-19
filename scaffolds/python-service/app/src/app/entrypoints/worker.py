"""Background worker loop: one tick, then wait; stops cleanly on the stop event."""

import asyncio
from collections.abc import Awaitable, Callable

from app.observability.logging import get_logger

log = get_logger(__name__)

Tick = Callable[[], Awaitable[None]]


async def run_worker(*, tick: Tick, poll_interval_s: float, stop: asyncio.Event) -> int:
    """Run `tick` until `stop` is set. Returns the number of ticks run.

    A failing tick is logged and the loop continues: one bad item must not stop the worker.
    """
    ticks = 0
    log.info("worker.started", poll_interval_s=poll_interval_s)
    while not stop.is_set():
        try:
            await tick()
        except Exception:
            log.exception("worker.tick_failed")
        ticks += 1
        try:
            await asyncio.wait_for(stop.wait(), timeout=poll_interval_s)
        except TimeoutError:
            continue
    log.info("worker.stopped", ticks=ticks)
    return ticks
