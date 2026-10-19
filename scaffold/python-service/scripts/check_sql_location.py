"""SQL-location guard: run by `make check`.

import-linter keeps `sqlalchemy` / `psycopg` imports inside `persistence/postgres`; this guard
also catches raw SQL strings anywhere else. Directories come from `scripts/guards.toml`.

Usage: python scripts/check_sql_location.py [ROOT]
"""

import re
import sys
from pathlib import Path

from _config import section

_SQL = re.compile(
    r"""exec_driver_sql|\btext\(\s*["']|["']\s*(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|"""
    r"""CREATE|DROP|ALTER|TRUNCATE)\s""",
)


def find_sql(root: Path, *, guarded_dirs: list[str], allowed: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    for guarded in guarded_dirs:
        base = root / guarded
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            if relative.startswith(allowed) or "__pycache__" in path.parts:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if _SQL.search(line):
                    found.append(f"{relative}:{number}: {line.strip()}")
    return found


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    config = section("sql_location")
    found = find_sql(
        root,
        guarded_dirs=config.get("guarded_dirs", []),
        allowed=tuple(config.get("allowed_prefixes", [])),
    )
    for entry in found:
        print(entry, file=sys.stderr)
    if found:
        print(
            f"sql-location guard: {len(found)} SQL string(s) outside persistence/postgres. "
            "Move the query into a Postgres repository.",
            file=sys.stderr,
        )
        return 1
    print("sql-location guard: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
