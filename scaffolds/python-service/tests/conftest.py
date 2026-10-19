"""Shared fixtures: frozen time, seeded ids, isolated logging.

Postgres tests are marked `db` and get a throwaway testcontainer (see
`tests/persistence/contracts/README.md`); never the developer database.
"""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from app.domain.clock import FrozenClock
from app.domain.ids import SeededIdGenerator
from app.observability.logging import reset_logging

FROZEN_AT = datetime(2026, 1, 1, 9, 30, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _isolated_logging() -> Iterator[None]:
    yield
    reset_logging()


@pytest.fixture
def frozen_clock() -> FrozenClock:
    return FrozenClock(FROZEN_AT)


@pytest.fixture
def seeded_ids() -> SeededIdGenerator:
    return SeededIdGenerator(seed=20260101)
