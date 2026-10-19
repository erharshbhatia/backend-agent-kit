"""Baseline: create schema `app`.

Revision ID: 0001
Revises:
Create Date: 2026-01-01
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS app")


def downgrade() -> None:
    raise NotImplementedError("forward-only migrations")
