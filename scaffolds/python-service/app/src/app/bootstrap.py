"""Composition root: the only module that picks concrete implementations.

Builds a frozen `Container` from `Settings`, then the API app, the worker, and the CLI.
"""

import asyncio
import signal
from dataclasses import dataclass

from fastapi import FastAPI

from app.domain.clock import Clock, SystemClock
from app.domain.ids import IdGenerator, UuidV7Generator
from app.entrypoints.api import build_api
from app.entrypoints.cli import build_cli
from app.entrypoints.worker import run_worker
from app.observability.logging import configure_logging, get_logger
from app.persistence.ports.database import Database
from app.persistence.ports.uow import UnitOfWork, UnitOfWorkFactory
from app.persistence.postgres.db import PostgresDatabase, create_engine
from app.persistence.postgres.uow import PostgresUnitOfWork
from app.settings import Settings

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    database: Database
    uow_factory: UnitOfWorkFactory
    clock: Clock
    ids: IdGenerator


def build_container(settings: Settings | None = None) -> Container:
    settings = settings if settings is not None else Settings()
    configure_logging(settings.logging)
    engine = create_engine(settings.db)

    def uow_factory() -> UnitOfWork:
        return PostgresUnitOfWork(engine)

    return Container(
        settings=settings,
        database=PostgresDatabase(engine),
        uow_factory=uow_factory,
        clock=SystemClock(),
        ids=UuidV7Generator(),
    )


def create_app() -> FastAPI:
    """uvicorn factory: `uvicorn app.bootstrap:create_app --factory`."""
    container = build_container()
    return build_api(database=container.database)


async def run_background_worker(container: Container) -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async def tick() -> None:
        # Replace with the worker's sweeps (claim due work with SKIP LOCKED, process, commit).
        log.debug("worker.tick")

    try:
        await run_worker(
            tick=tick, poll_interval_s=container.settings.worker.poll_interval_s, stop=stop
        )
    finally:
        await container.database.close()


def run_cli() -> None:
    """`appctl` console script."""
    container = build_container()

    async def ping() -> None:
        try:
            await container.database.ping()
        finally:
            await container.database.close()

    build_cli(run_worker=lambda: run_background_worker(container), ping_database=ping)()
