"""Alembic environment: schema `app`, compared against `postgres/tables.py`.

Migrations run on a synchronous psycopg 3 connection (same URL as the async engine).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from app.persistence.postgres.tables import SCHEMA, metadata
from app.settings import Settings

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def _database_url() -> str:
    # Tests pass the URL of their Postgres container; everyone else uses Settings.
    url = config.attributes.get("database_url")
    return url if isinstance(url, str) else Settings().db.url


def _include_name(name: str | None, type_: str, parent_names: object) -> bool:
    return name == SCHEMA if type_ == "schema" else True


def _run(connection: Connection) -> None:
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
    context.configure(
        connection=connection,
        target_metadata=metadata,
        version_table_schema=SCHEMA,
        include_schemas=True,
        include_name=_include_name,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_online() -> None:
    # Pin search_path so a role named like the schema doesn't hide it from `alembic check`.
    engine = create_engine(_database_url(), connect_args={"options": "-c search_path=public"})
    try:
        with engine.connect() as connection:
            _run(connection)
            connection.commit()
    finally:
        engine.dispose()


if context.is_offline_mode():
    raise SystemExit("offline (--sql) migrations are not supported; run against a database")
_run_online()
