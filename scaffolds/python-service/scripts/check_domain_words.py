"""Domain-word guard: run by `make check`.

Fails if a forbidden tenant, customer, or workflow word appears in generic code. Words and
guarded directories come from `scripts/guards.toml` [domain_words]. Words are matched as whole
identifier parts, so `invoice`, `Invoice`, `invoice_id`, and `invoiceTotal` match while
`invoiced_x` only matches if `invoiced` is listed.

Usage: python scripts/check_domain_words.py [ROOT]
"""

import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from _config import section

SCANNED_SUFFIXES = {".py", ".pyi", ".sql", ".yaml", ".yml", ".toml", ".json", ".ini", ".j2"}
SKIPPED_PARTS = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
# camelCase and snake_case split into parts; digits dropped.
_PART = re.compile(r"[A-Z]{2,}(?=s(?![a-z]))|[A-Z]+(?![a-z])|[A-Z]?[a-z]+")


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    word: str
    text: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: '{self.word}' in: {self.text.strip()}"


@dataclass(frozen=True, slots=True)
class AllowRule:
    path_glob: str
    word: str

    def allows(self, finding: Finding) -> bool:
        return finding.word == self.word and fnmatch(finding.path, self.path_glob)


def words_in(line: str, forbidden: frozenset[str]) -> Iterator[str]:
    for part in _PART.findall(line):
        if part.lower() in forbidden:
            yield part.lower()


def scan(root: Path, *, guarded_dirs: list[str], forbidden: frozenset[str]) -> list[Finding]:
    findings: list[Finding] = []
    for guarded in guarded_dirs:
        base = root / guarded
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
                continue
            if SKIPPED_PARTS.intersection(path.parts):
                continue
            relative = path.relative_to(root).as_posix()
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                findings.extend(
                    Finding(relative, number, word, line) for word in words_in(line, forbidden)
                )
    return findings


def load_rules(entries: list[dict[str, str]]) -> list[AllowRule]:
    rules: list[AllowRule] = []
    for entry in entries:
        if not entry.get("reason"):
            raise SystemExit(f"guards.toml: allow entry {entry} needs a reason")
        rules.append(AllowRule(path_glob=entry["path"], word=entry["word"].lower()))
    return rules


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    config = section("domain_words")
    guarded_dirs: list[str] = config.get("guarded_dirs", [])
    forbidden = frozenset(w.lower() for w in config.get("forbidden_words", []))
    rules = load_rules(config.get("allow", []))
    found = [
        f
        for f in scan(root, guarded_dirs=guarded_dirs, forbidden=forbidden)
        if not any(rule.allows(f) for rule in rules)
    ]
    for finding in found:
        print(finding.render(), file=sys.stderr)
    if found:
        print(
            f"domain-word guard: {len(found)} forbidden word(s) in generic code. Move the code "
            "to the tenant/extension package, or add a reasoned allow entry.",
            file=sys.stderr,
        )
        return 1
    note = "" if forbidden else " (no words configured yet)"
    print(f"domain-word guard: clean ({', '.join(guarded_dirs)}){note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
