"""structlog to stderr: console locally, JSON in containers.

Log events, not prose: `log.info("order.created", order_id=...)`. Never log secrets or PII.
Module loggers are `log = get_logger(__name__)` at import; bind extra context inside functions.
"""

import logging
import sys
from typing import TextIO, cast

import structlog
from structlog.typing import FilteringBoundLogger, Processor

from app.settings import LoggingSettings


def configure_logging(settings: LoggingSettings, *, stream: TextIO | None = None) -> None:
    """Configure structlog once, from the composition root. Tests pass a buffer as `stream`."""
    level = logging.getLevelNamesMapping()[settings.level]
    output = stream if stream is not None else sys.stderr
    renderer: Processor = (
        structlog.processors.JSONRenderer(default=str)
        if settings.format == "json"
        else structlog.dev.ConsoleRenderer(colors=output.isatty())
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            # Log timestamps are observability metadata, not domain time.
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=output),
        cache_logger_on_first_use=False,
    )


def reset_logging() -> None:
    """Back to structlog defaults (tests)."""
    structlog.reset_defaults()


def get_logger(name: str) -> FilteringBoundLogger:
    """A lazy logger that follows the current configuration."""
    return cast(FilteringBoundLogger, structlog.get_logger(name))
