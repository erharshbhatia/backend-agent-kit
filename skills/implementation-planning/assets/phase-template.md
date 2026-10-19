# P<NN>: <Phase title>

| | |
| --- | --- |
| Module(s) | `<package>/<module>/`, … |
| Depends on | P<NN> (<what it needs from it>) |
| Estimate | <n> wk |
| Requirements | <IDs this phase serves> |
| Outcome slice | <which part the current outcome needs, or "all"> |

## Goal

<Two or three sentences: what exists after this phase that did not before.>

## In scope

- <item>

## Out of scope

- <item> (→ P<NN> or later outcome)

## Modules and files

```text
<package>/src/<package>/<module>/
  port.<ext>       <interface(s)>
  <file>.<ext>     <purpose>
tests/<module>/
  test_<behaviour>.<ext>
```

These paths are the phase's ownership list: parallel agents must not edit files listed by another in-progress phase.

## Design details

<Semantics, algorithms (pseudocode), edge cases, idempotency and concurrency guarantees, failure handling. Link the HLD and spec sections rather than copying them.>

## Tables and repositories added

| Table / repository | Purpose | Spec section |
| --- | --- | --- |
| | | `database-schema.md` §<n> |

## Tasks

Order: ports and tests first, then adapters, then wiring. Each task ends green and becomes `P<NN>-T<n>` in the ledger.

1. <task>
2.

## Tests

- **Unit:** <domain logic>
- **Contract:** <each repository on the database and memory; each adapter against its mock>
- **Property / state machine:** <invariants, e.g. "a request delivered twice returns the same outcome", "a claim is taken by exactly one worker">
- **Scenario:** <end-to-end cases this phase enables>

## Exit criteria

- [ ] <checkable statement>
- [ ] `check` green.

## Decisions to review

Each with a recommended default. Tasks that depend on an open decision do not start until it is resolved.

1. <Question>? Recommended: <default>, because <why>.
2.

<!-- After resolution, rewrite as:
1. ~~<Question>?~~ **Resolved:** <answer> (<who>, YYYY-MM-DD; ADR-NNNN).
-->

<!-- After build, append above "Decisions to review":

## As built (YYYY-MM-DD, M<n>, [change record](../docs/changes/YYYY/…), [ADR-NNNN](../docs/decisions/…))

Built: <what>. Deferred: <what, with follow-up ids>. Files differ from the plan as follows: <…>.

Interfaces later phases rely on:

| Need | Use |
| --- | --- |
| <capability> | `<package>.<module>.<Symbol>`: `<signature>` |
-->
