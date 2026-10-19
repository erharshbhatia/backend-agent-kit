"""S0: the service boots and answers.

End-to-end scenarios live here, one module per scenario id (`make e2e`). They go through the
real entrypoints with outside systems mocked and the clock frozen; scenarios that need Postgres
are marked `db`. This one needs nothing but the memory twins, so it also runs in `make check`.
"""

import asyncio

import httpx

from app.entrypoints.api import build_api
from app.entrypoints.worker import run_worker
from app.persistence.memory.uow import MemoryDatabase


async def test_s0_api_answers_and_worker_ticks_then_stops() -> None:
    # The API, through the real router, over the memory database twin.
    transport = httpx.ASGITransport(app=build_api(database=MemoryDatabase()))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/livez")).status_code == 200
        assert (await client.get("/readyz")).json() == {"ready": True, "checks": {"database": "ok"}}

    # The worker loop, through the real runner: one tick, then a clean stop.
    stop = asyncio.Event()

    async def tick() -> None:
        stop.set()

    assert await run_worker(tick=tick, poll_interval_s=0.001, stop=stop) == 1
