# Invariants

Rules no change may break. If a task seems to require breaking one, stop: it needs a decision record (ADR) and the owner's agreement first.

<!-- The baseline below applies to any service built with this kit. Keep the numbers stable: changes, ADRs and reviews cite them ("INVARIANTS #7"). Add project rules in the last section; remove a baseline rule only with an ADR. -->

## Code structure

1. **Hexagonal layering.** Domain is pure; ports are interface types; adapters implement ports; only the composition root (named in `STACK.md`) wires implementations.
2. **Repository pattern.** All database access goes through repositories inside a unit of work. Only the persistence adapter package contains SQL. Repositories never commit, never call each other, and hold no business logic. Every repository has a memory twin that passes the same contract suite.
3. **Vendor isolation.** Each vendor SDK (database driver, LLM client, HTTP client for a partner, template engine) is imported only inside its adapter module. Vendor types never cross the adapter edge. The allowed import locations are listed in the import-linter config.
4. **Time and IDs are injected** (`Clock`, `IdGenerator`, time-ordered unique ids). No database clock in queries, no wall-clock reads or random IDs in domain or application code.
5. **Extend by registering, not branching.** New kinds of things (handlers, integrations, channels, rules) are added through registries; no `if kind == ...` chains outside a registry.
6. **The core stays generic.** No tenant, customer, or business-flow words in the core package (`<package>`), its tables, or its repository names. They live in tenant/integration packages, configuration, and tests. A domain-word guard in `make check` enforces the list `<domain-words>`.

## Data and runtime correctness

7. **One writer per aggregate.** Concurrent work on the same record is prevented by a lease or optimistic version check, never by hope. Lost races raise a typed conflict.
8. **Everything idempotent at boundaries.** Inbound requests (client or provider message id), events (source + event id), queued work (dedupe key), outbound messages (dedupe key) and external writes (derived idempotency key) can arrive twice and have the effect once.
9. **External writes follow a recorded-intent protocol.** Intent is stored before the call with a stable idempotency key; an unknown outcome is reconciled or handed to a human, never blindly retried with a new key; compensation is a separate, audited write.
10. **Durable state survives crashes.** Work in progress is checkpointed so a restart resumes from the last checkpoint; no completed step runs twice. Queue claims use the store's atomic claim primitive (e.g. `FOR UPDATE SKIP LOCKED` in Postgres) or a lease.
11. **Unknown is not false.** Missing, stale, or failed facts are represented explicitly (`UNKNOWN`, a typed failure), never silently coerced to `false`, `0`, or empty.
12. **Truthful outcomes.** The system never reports that an action succeeded (to a user, a caller, or a log meant for operators) without a confirmed outcome of that action.

## AI and safety (if the project uses models)

13. **The model proposes, deterministic code decides.** A model output never directly authorizes a write or an irreversible action; validated, typed decisions pass through deterministic policy first.
14. **Deterministic arithmetic.** Amounts, comparisons, totals and dates are computed in code, never by a model.
15. **Model test policy is decided by ADR** (real calls vs recorded fixtures vs fakes) and applied everywhere the same way.

## Process

16. **Every change is documented** (change record; ADR for decisions), and every design doc stays true to the code in the same change.
17. **No task is built while a "Decision to review" it depends on is unresolved.** Settled ones are reconciled against ADRs without asking; open ones are asked in one batch (`sdlc-workflow` Stage 1).
18. **Checks are never reported green unless they were run and seen green.** Real command output goes in the change record.
19. **Never silence a check to get green** (ignore comments, linter exceptions, skipped tests). Fix the design, or raise an ADR to change the rule.

## Project-specific invariants

<!-- Add numbered rules from 20 up. Each cites the ADR that created it. Examples of the kind of rule that belongs here (neutral sample domain):
20. **An order is never charged twice** — the payment write uses the order id as its idempotency key (ADR-NNNN).
21. **Published versions are immutable** — editing creates a new version (ADR-NNNN).
-->
