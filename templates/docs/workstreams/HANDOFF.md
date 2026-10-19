# Handoff — read this first in a new session

| | |
| --- | --- |
| Updated | YYYY-MM-DD — <agent/session> |
| Current outcome | [<Outcome NN: title>](../../implementation/outcome-NN-<slug>.md), milestone M<n> |
| Isolation mode | worktree · copy (see the isolation ADR) |
| Off-limits | <developer database host:port, compose volumes, servers the owner is using> |

## Where we are

<!-- One line per integrated piece, newest first: what landed, when, the verified numbers. -->

- YYYY-MM-DD: <what> integrated. Verified: `check` <n> passed, `test-db` <n>, `e2e` <n>.

## In flight

<!-- Every worker or session that has not been integrated, so the next coordinator can resume it instead of restarting it. -->

| Task | Agent | Worktree / copy | Patch state | Next step |
| --- | --- | --- | --- | --- |
| PNN-Tn | <id> | <path> | none · checkpoint at <path> · final at <path> | |

## Needs the owner

- <decision or approval, with the recommended default> — or "Nothing".

## Next action

1. <The exact first thing the next session does.>

## Gotchas

<!-- What bit this session and is still true: port clashes, lock-file merges, a doc that disagrees with the code. Delete a line when it is fixed. -->

- <gotcha>
