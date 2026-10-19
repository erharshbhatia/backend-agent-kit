# Repository contract suites

One suite per repository port, named `test_<port module>.py`, parameterized over both
implementations: `postgres` (a throwaway testcontainer, marked `db`) and `memory`. The
repository guard (`scripts/check_repositories.py`) fails `make check` when a port has no suite.

Each suite covers: the normal path, idempotent insert (`Created` / `Existing`), version
conflict, concurrent claims (`SKIP LOCKED`), pagination limits, and frozen time.

Postgres fixture shape (add to `tests/conftest.py` when the first repository lands):

```python
from alembic import command
from alembic.config import Config
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    with PostgresContainer("postgres:16-alpine", driver="psycopg") as container:
        url = container.get_connection_url()
        config = Config("alembic.ini")
        config.attributes["database_url"] = url
        config.attributes["configure_logger"] = False
        command.upgrade(config, "head")
        yield url
```
