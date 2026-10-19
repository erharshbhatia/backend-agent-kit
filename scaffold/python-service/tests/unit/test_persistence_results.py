"""Typed repository results and failures behave as the data-access standard says (R8 to R10)."""

from app.persistence.ports.errors import ConcurrencyConflict, LeaseLost, PersistenceError
from app.persistence.ports.results import Created, Existing, InsertResult, Page


def describe(result: InsertResult[str]) -> str:
    match result:
        case Created(value):
            return f"created {value}"
        case Existing(value):
            return f"existing {value}"


def test_insert_result_variants_are_distinguished_by_match() -> None:
    assert describe(Created("a")) == "created a"
    assert describe(Existing("a")) == "existing a"


def test_page_marks_the_last_page_with_no_cursor() -> None:
    last = Page(items=("x", "y"), next_cursor=None)
    assert last.items == ("x", "y")
    assert last.next_cursor is None


def test_persistence_failures_carry_ids_and_share_a_base() -> None:
    conflict = ConcurrencyConflict("order", "o-1", expected_version=3)
    lost = LeaseLost("job", "j-9", owner="worker-2")
    assert isinstance(conflict, PersistenceError)
    assert isinstance(lost, PersistenceError)
    assert "o-1" in str(conflict)
    assert "3" in str(conflict)
    assert lost.owner == "worker-2"
