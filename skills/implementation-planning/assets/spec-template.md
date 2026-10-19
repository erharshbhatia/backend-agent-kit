# <Spec name>: <Project>

| | |
| --- | --- |
| Status | Draft for review · Binding |
| Applies to | <which code / phases must follow it> |
| Source of truth in code | <the schema source of truth → migrations, as STACK.md names them> |
| Covers | <phases / components> |

---

## 1. How this was designed

<Show the derivation so reviewers can check the reasoning. For a database schema:>

| Step | What was done | Where |
| --- | --- | --- |
| 1. Entities | Every entity the system owns; what external systems own is referenced, not stored | §4 |
| 2. Access patterns | Every query, from each repository method: what it reads/writes, how often, under what concurrency | §7 |
| 3. Model and normalize | One table per entity, 3NF; JSONB only for data written and read whole and never filtered on the hot path | §3, §5 |
| 4. Invariants in the database | Every business-critical guarantee (dedupe, one-active, consistency) is a UNIQUE, CHECK, or FK | §5 |
| 5. Indexes from patterns | Every index maps to a named access pattern; no speculative indexes | §7 |
| 6. Concurrency | Optimistic versions, leases with fencing, atomic claims (e.g. `SKIP LOCKED`) | §8 |
| 7. Volume and lifecycle | Growth from the HLD estimates; hot vs append-only; partitioning and retention | §9 |
| 8. Privacy | PII columns marked; tenant column for later row-level security | §10 |
| 9. Evolution | Migration order per phase; expand/contract | §11 |

## 2. Principles

1. <rule with a one-line why>

## 3. <Format-specific sections>

<For a schema: entity map, tables (DDL per phase), enumerations, access patterns → indexes, concurrency and idempotency mechanisms, volume and retention, privacy, migration plan.>
<For a data-access standard: structure, interfaces, rules R1–Rn, per-entity catalog, testing, review checklist.>
<For a file / wire format: vocabulary, document structure, every field with type and meaning, validation rules with IDs, versioning, examples.>

## N. Changes this doc makes to earlier plans

| Doc | Change |
| --- | --- |
| | |

## N+1. Decisions to review

1. <Question>? Recommended: <default>.
