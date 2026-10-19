---
name: engineering-standards
description: Binding low-level design and code standards for this repo — hexagonal layering (ports and adapters), the repository pattern with unit of work, registries for extension, typed contracts, clean code (typing, naming, errors as values, small modules), vendor isolation, injected time and IDs, and the testing pyramid. Use whenever you write, modify, refactor, or review ANY code, tests, SQL, migrations, adapters, integrations, endpoints, workers, or interfaces in this repo — including small fixes and "quick" changes — and before submitting work for review. Also use when deciding where new code should live or how two modules should talk to each other.
---

# Engineering standards

The system must absorb months of new features, integrations, and vendor changes without turning into a tangle. These standards are how: every rule below exists to keep a change local to one module and testable in isolation. When a rule seems to get in the way, that is usually a sign the code wants to live somewhere else. Find that place rather than bending the rule.

The rules are stack-agnostic. The concrete names behind the abstract ones used here (commands such as `check`, tools such as the layer-contract tool, files such as the composition root) are in `project-guide/knowledge/STACK.md`. Idioms and code for that stack are in `references/stacks/<profile>.md`; the profile is chosen by the stack ADR at bootstrap (`project-bootstrap`). One profile exists today: `references/stacks/python-postgres.md`.

## The ten rules

1. **Layers point inward.** `entrypoints → application → domain`; adapters implement ports; `domain` imports nothing with I/O. Only the composition root chooses implementations. → `references/lld.md`
2. **Depend on ports, not vendors.** The database driver, model/LLM SDKs, partner HTTP clients, template engines and queues live behind interface types, imported only inside their adapter module. → `references/lld.md`
3. **All data access through repositories inside a unit of work.** Intent-named methods, domain models in and out, no commits in repositories, no SQL outside the persistence adapter package, a memory twin for every repository, one contract suite for both. → `references/repository.md`
4. **Extend by registering, not by branching.** New handlers, integration operations, channels, validation rules and similar "kinds of things" are added through registries; no `if kind == ...` chains outside a registry.
5. **Contracts are typed models.** Typed boundary models at every boundary; discriminated unions for variants; no untyped map or dictionary crossing a module boundary.
6. **Errors are values at integration edges.** Integrations return a typed result (success | failure with category); model adapters return typed failures; exceptions are for bugs and infrastructure faults.
7. **Business logic is pure with respect to storage.** Handlers and domain functions read their inputs and return results or effects; the use case or runtime persists them.
8. **Inject time and IDs.** A `Clock` and an `IdGenerator` only; nothing reads the wall clock or generates random IDs inline.
9. **Speak the project vocabulary.** Use the terms in `project-guide/knowledge/GLOSSARY.md`; retired terms listed there are banned as system names. No tenant or customer words in the core package (the list in `project-guide/knowledge/INVARIANTS.md` #6 and the domain-word guard's configuration).
10. **Every behaviour has a test at its layer.** Domain unit tests; application tests with fakes and memory repositories; adapter contract tests; end-to-end scenarios. Model calls follow the project's test-policy ADR. → `references/testing.md`

Clean-code conventions (naming, function size, comments, async, logging, config, dependencies) are in `references/clean-code.md`.

## Before you write code

- Find the phase doc and the design section for what you are building; follow the file layout it names.
- Decide which layer the code belongs to and which port it talks through (`references/lld.md` §5). If no port fits, propose one in the design note (`sdlc-workflow`) instead of reaching across layers.
- If the change touches a table, read `implementation/database-schema.md` and `references/repository.md` first.
- Read the stack profile once per session for the idioms and the code shapes (`references/stacks/<profile>.md`).

## Before you hand over

Run through `references/review-checklist.md`. It is the same list a reviewer will use, so running it yourself saves a review round.

## Enforced by tools

`check` (STACK.md) needs no Docker and no external keys: the linter and formatter, the type checker in its strictest mode, the layer-contract tool (layer and vendor contracts), the banned-API tool (wall clock, random ids, environment reads), the domain-word, SQL-location and repository guards (R11), and every test not tagged `db` or `external`. `check-all` adds `test-db` (database tests on a throwaway container) and `migrations-check`; run it for any persistence, schema or runtime change. Never silence a failure with an ignore comment or a linter exception to get green; fix the design. If you believe a rule is wrong, raise it as an ADR (`change-records`). Which tool enforces which rule is listed in the stack profile; the scaffold that sets them up is described in `project-bootstrap`.
