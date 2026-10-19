# <Title: what changed, in plain words>

| | |
| --- | --- |
| Date | YYYY-MM-DD |
| Phase / area | e.g. P04 · persistence |
| Change type | phase-task · feature · bugfix · integration · schema · runtime · interface · model · dependency · refactor · security-sensitive · config · docs-only |
| Task | Ledger task id, e.g. P04-T3 |
| Requirements | e.g. OR-12, X-3, INVARIANTS #8 (or "None") |
| ADR | ADR-NNNN (or "None") |
| Agent / session | who did the work |
| Approved by | owner + date, when the change type requires approval (or "Not required") |
| Status | In progress · Done · Reverted |

## Summary
Two or three sentences a reader can stop after.

## Why
The requirement, failure, or decision that motivated this change.

## Design
(Written at Stage 2 as the design note.)
- Where the code lives (layer, modules):
- Ports / signatures added or changed:
- Data / schema changes:
- Idempotency and concurrency:
- Failure cases and edge cases:
- Alternatives considered:

## Changes
| File / area | Change |
| --- | --- |
| | |

## Schema and migrations
Migration id(s), tables/columns/indexes, repository methods added (or "None").

## Tests
New or changed tests, by layer, with scenario / requirement IDs.

## Verification
```text
$ <check command from STACK.md, e.g. make check>
<result summary: passed/failed counts>
$ <other suites the change type requires>
<result summary>
```
Acceptance criteria and exit criteria covered: ✓/✗ each.

## Deviations
From the phase doc, the standards, or the design note — with reasons (or "None").

## Docs updated
List every doc changed to stay true (or "None needed", with why).

## Risks and rollback
What could go wrong; how to undo it.

## Follow-ups
Concrete items, each also added to the ledger (or "None").
