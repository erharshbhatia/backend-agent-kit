"""Typed persistence failures (engineering-standards repository.md, R8).

Repositories raise these on purpose; callers decide what to do (retry the use case, hand the
work to someone else, report a conflict). Everything else a repository raises is a bug or an
infrastructure fault.
"""


class PersistenceError(Exception):
    """Base of every failure a repository raises deliberately."""


class ConcurrencyConflict(PersistenceError):
    """The row's version moved since it was read: another writer won (INVARIANTS #7)."""

    def __init__(self, entity: str, entity_id: object, *, expected_version: int) -> None:
        super().__init__(
            f"{entity} {entity_id}: expected version {expected_version}, but the row moved"
        )
        self.entity = entity
        self.entity_id = entity_id
        self.expected_version = expected_version


class LeaseLost(PersistenceError):
    """The lease on a row expired or was taken by another owner before this write."""

    def __init__(self, entity: str, entity_id: object, *, owner: str) -> None:
        super().__init__(f"{entity} {entity_id}: lease no longer held by {owner}")
        self.entity = entity
        self.entity_id = entity_id
        self.owner = owner
