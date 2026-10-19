#!/usr/bin/env bash
# SessionStart hook: in a project built with the kit, point the session at the resume file.
# Prints nothing elsewhere, so a globally installed plugin stays quiet in unrelated repos.
set -u
handoff="docs/workstreams/HANDOFF.md"
if [ ! -f "$handoff" ] && [ ! -d ".claude/skills/project-guide" ]; then
  exit 0
fi
echo "backend-agent-kit: this project uses the kit. Plugin root: ${CLAUDE_PLUGIN_ROOT:-unknown} (templates/, scaffolds/ live there)."
echo "Orient with the project-guide skill, then read docs/workstreams/HANDOFF.md before anything else."
if [ -f "$handoff" ]; then
  echo "--- $handoff (first 40 lines) ---"
  head -40 "$handoff"
  echo "--- end ---"
fi
exit 0
