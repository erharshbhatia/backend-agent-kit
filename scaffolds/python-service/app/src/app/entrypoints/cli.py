"""Operator CLI (`appctl`). Commands receive their dependencies from the composition root."""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

import typer


def build_cli(
    *,
    run_worker: Callable[[], Coroutine[Any, Any, None]],
    ping_database: Callable[[], Coroutine[Any, Any, None]],
) -> typer.Typer:
    cli = typer.Typer(no_args_is_help=True, help="<Project> operator CLI.")

    @cli.command()
    def worker() -> None:
        """Run the background worker until interrupted."""
        asyncio.run(run_worker())

    @cli.command("db-ping")
    def db_ping() -> None:
        """Check that the database is reachable."""
        asyncio.run(ping_database())
        typer.echo("database: ok")

    return cli
