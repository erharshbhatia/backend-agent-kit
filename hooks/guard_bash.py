"""PreToolUse guard for Bash in kit projects: the multi-agent safety rules, enforced mechanically.

Reads the hook payload on stdin, exits 2 with a reason on stderr to block, 0 to allow. Active only
when the working directory looks like a kit project (HANDOFF.md or the project-guide skill exists),
so a globally installed plugin does not interfere elsewhere. Escape hatch for the owner: prefix the
command with `KIT_ALLOW=1`.
"""

import json
import os
import re
import sys

RULES: list[tuple[str, str]] = [
    (r"\bpkill\b|\bkillall\b", "Never kill processes by name or pattern; it takes down other agents' and the owner's servers. Stop only processes you started, by PID."),
    (r"\bgit\s+push\b[^|;&]*\s(--force|-f|--force-with-lease)\b", "Force-pushing a shared branch needs the owner's explicit approval; ask, do not push."),
    (r"\bdocker\s+compose\b[^|;&]*\bdown\b[^|;&]*\s(-v|--volumes)\b|\bdocker\s+volume\s+(rm|prune)\b", "This deletes a database volume that may be the developer database. Use your own throwaway database."),
    (r"\bdropdb\b|\bDROP\s+(DATABASE|SCHEMA)\b", "Dropping a database or schema may hit the developer database. Use a throwaway database; ask the owner otherwise."),
    (r"\bgit\s+reset\s+--hard\b|\bgit\s+clean\s+-[a-zA-Z]*f", "This discards work in the tree, possibly another agent's. Look first; revert specific files instead."),
]


def is_kit_project() -> bool:
    return os.path.exists("docs/workstreams/HANDOFF.md") or os.path.isdir(".claude/skills/project-guide")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    if not command or "KIT_ALLOW=1" in command or not is_kit_project():
        return 0
    for pattern, reason in RULES:
        if re.search(pattern, command, flags=re.IGNORECASE):
            sys.stderr.write(
                f"backend-agent-kit guard blocked this command. {reason} "
                "If the owner wants it anyway, they can run it themselves or prefix it with KIT_ALLOW=1.\n"
            )
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
