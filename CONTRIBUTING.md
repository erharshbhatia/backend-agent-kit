# Contributing

Three kinds of contribution are worth the most right now, in this order.

1. **A wave metrics row.** Run the kit on real work, then open a discussion or issue titled "Wave metrics: <project type>" and paste the row from your `HANDOFF.md` (launched, returned, lost, verified, anchor-red, must-fix findings, agents, tokens, `check-all` after integration) plus one sentence on what the workflow got wrong. These rows are the benchmark; there is nothing else.
2. **A stack.** A profile (`skills/engineering-standards/references/stacks/<name>.md`, contract in that folder's README) plus a scaffold (`scaffolds/<name>/`, contract in `scaffolds/CONTRACT.md`). `scaffolds/check-contract.sh <name>` must pass and `make check` must be green on a clean machine with no Docker. TypeScript and Go are the open requests.
3. **A fix to a skill that was wrong in practice.** Say what happened, in which project, and what the agent did instead. A skill edit without a failure behind it is usually a style preference; those are fine, but say so.

## Rules

The kit's own `CLAUDE.md` is binding for every change: generic skills name no project, stack, tool or command; one canonical copy of each list; templates and scaffolds updated with the skill that changed; versions bumped and `CHANGELOG.md` extended with a "Project side" line.

Before opening a pull request, run and paste the output of:

```bash
claude plugin validate .
scaffolds/check-contract.sh python-service      # and any scaffold you touched
cd scaffolds/python-service && uv sync && make check
node --check workflows/wave.js
```

Keep `WORKER_REPORT` in `workflows/wave.js` identical to `skills/multi-agent-development/references/worker-report-schema.json`.

## Style

Short sentences, tables over prose, no em-dashes, no placeholders like `<package>` outside `templates/` and scaffold `BOOTSTRAP.md` files. Say what breaks and why before saying what to do.
