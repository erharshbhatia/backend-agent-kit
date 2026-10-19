"""Shared loader for scripts/guards.toml."""

import tomllib
from pathlib import Path
from typing import Any

CONFIG = Path(__file__).with_name("guards.toml")


def section(name: str) -> dict[str, Any]:
    with CONFIG.open("rb") as handle:
        data: dict[str, Any] = tomllib.load(handle)
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise SystemExit(f"{CONFIG}: [{name}] must be a table")
    return value
