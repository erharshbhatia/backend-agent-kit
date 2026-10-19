# Review checklist

Use it on your own diff before handing over, and when reviewing someone else's. Every "no" needs a fix or a written reason in the change record. Tool and command names are the abstract ones from `project-guide/knowledge/STACK.md`.

Review lenses (`multi-agent-development`, three fresh reviewers for heavy change types): **correctness** = Correctness + Security; **invariants** = Design + Data + Documentation; **tests** = Tests + Code quality. One reviewer with no lens covers all sections.

## Design
- [ ] Code sits in the layer and module the phase doc / `lld.md` §5 names; dependencies point inward.
- [ ] New behaviour added through a registry or port, not a branch in central code.
- [ ] No tenant, customer, or business-flow words in the core package (domain-word guard passes).
- [ ] Project vocabulary used; no retired terms from `GLOSSARY.md`.
- [ ] A changed published interface (port, API, event, file format) has an ADR.

## Correctness
- [ ] Writes to outside systems use the recorded-intent protocol with a derived, stable idempotency key.
- [ ] Every boundary the change touches is idempotent (inbound request, event, queued work, outbox, external write).
- [ ] Missing or stale facts produce `UNKNOWN` or a typed failure and are handled; no silent `false`.
- [ ] No success reported without a confirmed outcome.
- [ ] Concurrency: one writer per aggregate (lease or version check); claims use the store's atomic claim primitive.
- [ ] Model output never authorizes a write directly (if the project uses models).
- [ ] Time and IDs injected; no wall clock or random IDs inline.

## Data
- [ ] All database access via repositories in a unit of work; no SQL outside the persistence adapter package.
- [ ] Schema change has migration + mapper + memory twin + contract tests, and `database-schema.md` is updated.
- [ ] Every list method bounded.

## Code quality
- [ ] Types strict; boundaries are typed boundary models; no "any" leaks.
- [ ] Errors are typed values at edges; nothing swallowed.
- [ ] Names clear; modules small and single-purpose; no dead or commented-out code.
- [ ] Comments explain why and cite requirement IDs; no change-history comments; TODOs carry a follow-up id.
- [ ] Logs structured, IDs bound, no PII or secrets.

## Security
- [ ] Inputs validated at the boundary; auth and tenant scoping checked on every new endpoint.
- [ ] Webhooks verify signatures; secrets come from the settings module only.

## Tests
- [ ] A failing test reproduced the bug before the fix (for bugs).
- [ ] Tests at the right layer; deterministic; named after behaviour; requirement/scenario IDs cited.
- [ ] Model tests follow the project's test-policy ADR.
- [ ] `check` passes locally (`check-all` for persistence, schema or runtime changes), plus every suite the change type requires; output pasted in the change record.

## Documentation
- [ ] Change record written; ADR for any decision; ledger updated.
- [ ] Design docs and `project-guide` knowledge files updated where behaviour, architecture, invariants, or vocabulary changed.
