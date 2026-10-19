"""Repository-completeness guard: run by `make check`.

Every repository port (a class named `<Name>Repository` in `persistence/ports/<module>.py`) must
have a `Postgres<Name>Repository`, a `Memory<Name>Repository`, and a shared contract suite
`tests/persistence/contracts/test_<module>.py`. Directories come from `scripts/guards.toml`.

Usage: python scripts/check_repositories.py [ROOT]
"""

import ast
import sys
from pathlib import Path

from _config import section


def classes_in(directory: Path) -> set[str]:
    names: set[str] = set()
    if not directory.is_dir():
        return names
    for path in directory.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names.update(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    return names


def ports(directory: Path) -> list[tuple[str, str]]:
    """(module stem, repository name without the `Repository` suffix) for every port."""
    found: list[tuple[str, str]] = []
    for path in sorted(directory.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name.endswith("Repository"):
                found.append((path.stem, node.name.removesuffix("Repository")))
    return found


def missing(root: Path) -> list[str]:
    config = section("repositories")
    postgres = classes_in(root / config["postgres_dir"])
    memory = classes_in(root / config["memory_dir"])
    contracts = root / config["contracts_dir"]
    problems: list[str] = []
    for module, name in ports(root / config["ports_dir"]):
        if f"Postgres{name}Repository" not in postgres:
            problems.append(f"{name}Repository: no Postgres{name}Repository")
        if f"Memory{name}Repository" not in memory:
            problems.append(f"{name}Repository: no Memory{name}Repository")
        if not (contracts / f"test_{module}.py").is_file():
            problems.append(
                f"{name}Repository: no contract suite {contracts.name}/test_{module}.py"
            )
    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    problems = missing(root)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(
            f"repository guard: {len(problems)} gap(s). Every port needs Postgres + memory "
            "implementations and one contract suite run against both.",
            file=sys.stderr,
        )
        return 1
    print("repository guard: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
