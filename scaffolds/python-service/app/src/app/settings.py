"""All settings (pydantic-settings). The only module that reads the environment.

Variables use the `APP_` prefix with `__` for nesting (`APP_DB__URL`, `APP_LOGGING__FORMAT`).
A `.env` file in the working directory is loaded too.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class DatabaseSettings(BaseModel):
    """Postgres connection and pool."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # repr=False: the URL carries the password; keep it out of reprs and logs.
    url: str = Field(default="postgresql+psycopg://app:app@localhost:55432/app", repr=False)
    pool_size: int = Field(default=5, ge=1)
    max_overflow: int = Field(default=5, ge=0)
    pool_timeout_s: float = Field(default=10.0, gt=0)
    connect_timeout_s: int = Field(default=5, ge=1)
    statement_timeout_ms: int = Field(default=15_000, ge=0)
    pool_recycle_s: int = Field(default=1800, ge=-1)
    echo_sql: bool = False


class LoggingSettings(BaseModel):
    """Structured logs: human-readable console locally, JSON in containers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: LogLevel = "INFO"
    format: Literal["console", "json"] = "console"


class WorkerSettings(BaseModel):
    """Background worker loop."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    poll_interval_s: float = Field(default=1.0, gt=0)


class Settings(BaseSettings):
    """Root settings, built once by the composition root and passed down through the container."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    db: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    worker: WorkerSettings = WorkerSettings()
