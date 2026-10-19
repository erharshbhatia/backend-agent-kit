---
name: engineering-standards
description: Binding low-level design and code standards for this repo — hexagonal layering (ports and adapters), the repository pattern with unit of work, registries for extension, typed contracts, clean Python (typing, naming, errors as values, small modules), vendor isolation, injected time and IDs, and the testing pyramid. Use whenever you write, modify, refactor, or review ANY code, tests, SQL, migrations, adapters, integrations, endpoints, workers, or interfaces in this repo — including small fixes and "quick" changes — and before submitting work for review. Also use when deciding where new code should live or how two modules should talk to each other.
---

# Engineering standards

The system must absorb months of new features, integrations, and vendor changes without turning into a tangle. These standards are how: every rule below exists to keep a change local to one module and testable in isolation. When a rule seems to get in the way, that's usually a sign the code wants to live somewhere else — find that place rather than bending the rule.

The default stack is Python 3.12, uv, FastAPI, SQLAlchemy async + psycopg3, Alembic, Pydantic v2, structlog, pytest + Hypothesis + testcontainers, ruff, mypy `--strict`, import-linter. A project may change the stack by ADR; the rules stay.

## The ten rules

1. **Layers point inward.** `entrypoints → application → domain`; adapters implement ports; `domain` imports nothing with I/O. Only `bootstrap.py` chooses implementations. → `references/lld.md`
2. **Depend on ports, not vendors.** The database driver, model/LLM SDKs, partner HTTP clients, template engines and queues live behind Protocols, imported only inside their adapter module. → `references/lld.md`
3. **All data access through repositories inside a unit of work.** Intent-named methods, domain models in and out, no commits in repositories, no SQL outside `persistence/postgres`, a memory twin for every repository, one contract suite for both. → `references/repository.md`
4. **Extend by registering, not by branching.** New handlers, integration operations, channels, validation rules and similar "kinds of things" are added through registries; no `if kind == ...` chains outside a registry.
5. **Contracts are typed models.** Pydantic v2 at every boundary; discriminated unions for variants; no `dict[str, Any]` crossing a module boundary.
6. **Errors are values at integration edges.** Integrations return a typed result (success | failure with category); model adapters return typed failures; exceptions are for bugs and infrastructure faults.
7. **Business logic is pure with respect to storage.** Handlers and domain functions read their inputs and return results or effects; the use case or runtime persists them.
8. **Inject time and IDs.** `Clock` and `IdGenerator` only; nothing reads the wall clock or generates random IDs inline.
9. **Speak the project vocabulary.** Use the terms in `project-guide/knowledge/GLOSSARY.md`; retired terms listed there are banned as system names. No tenant or customer words in the core package (the list in `project-guide/knowledge/INVARIANTS.md` #6 and `scripts/guards.toml`, enforced by the domain-word guard).
10. **Every behaviour has a test at its layer.** Domain unit tests; application tests with fakes and memory repositories; adapter contract tests; end-to-end scenarios. Model calls follow the project's test-policy ADR. → `references/testing.md`

Clean-code conventions (naming, function size, comments, async, logging, config, dependencies) are in `references/clean-code.md`.

## Before you write code

- Find the phase doc and the design section for what you are building; follow the file layout it names.
- Decide which layer the code belongs to and which port it talks through (`references/lld.md` §5). If no port fits, propose one in the design note (`sdlc-workflow`) instead of reaching across layers.
- If the change touches a table, read `implementation/database-schema.md` and `references/repository.md` first.

## Before you hand over

Run through `references/review-checklist.md`. It is the same list a reviewer will use, so running it yourself saves a review round.

## Enforced by tools

`make check` needs no Docker and no external keys: ruff (lint + format check), mypy `--strict`, import-linter (layer and vendor contracts), the domain-word, SQL-location and repository-completeness (R11) guards, and pytest excluding tests marked `db` or `external`. `make check-all` adds `make test-db` (Postgres tests, testcontainers) and `make migrations-check` (`alembic check`, after `make up && make migrate`); run it for any persistence, schema or runtime change. Never silence a failure with an ignore comment or a linter exception to get green; fix the design. If you believe a rule is wrong, raise it as an ADR (`change-records`). The scaffold that sets these tools up is described in `project-bootstrap`.
