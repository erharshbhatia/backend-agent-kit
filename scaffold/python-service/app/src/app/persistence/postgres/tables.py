"""SQLAlchemy Core tables: the schema Alembic migrations are checked against (`alembic check`).

Schema change = this file + an Alembic migration + mapper + memory twin + contract suite.
"""

from sqlalchemy import MetaData

SCHEMA = "app"

metadata = MetaData(schema=SCHEMA)
