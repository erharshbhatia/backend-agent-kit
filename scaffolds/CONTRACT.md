# Scaffold contract

Every directory under `scaffolds/` is a runnable service skeleton for one stack. The process skills never name a stack; they rely on each scaffold providing the same things under the same abstract names. `check-contract.sh <scaffold>` verifies the mechanical part.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | What is inside, the commands, how to run it |
| `STACK.md` | Filled copy of `templates/project-guide/knowledge/STACK.md`: every abstract command, tool and file name resolved for this stack. Bootstrap copies it into the project |
| `BOOTSTRAP.md` | The renames to do when the scaffold is copied into a project (package name, env prefix, CLI name, schema, image and compose names) and the grep that proves they are done |
| `Makefile` | The task runner with the targets below. A stack may delegate to its own runner inside each target |

## Makefile targets (the abstract commands)

`check`, `check-all`, `test`, `test-db`, `test-external`, `e2e`, `migrations-check`, `sync` (deps-sync), `lock` (deps-lock), `up`, `migrate`, `stack`, `down`.

`check` runs with no Docker and no keys on a clean machine. `test-external` exits 0 while no external tests exist.

## What the code ships

- Layers that point inward, enforced by a layer-contract tool.
- `Clock` and `IdGenerator` (time-ordered unique ids) injected; the wall clock, random ids and environment reads banned outside their adapters by a banned-API rule.
- `Database` and `UnitOfWork` ports, a database and a memory implementation of each, typed persistence failures (`ConcurrencyConflict`, `LeaseLost`) and results (`Created | Existing`, `Page`).
- A migration baseline and a `migrations-check` that fails when the schema source of truth and the migrations disagree.
- The three guards: domain words, SQL location, repository completeness (every repository port has a database twin, a memory twin and a contract suite).
- Structured logging with correlation ids, JSON in containers.
- `/livez` and `/readyz`, a worker loop that survives a failing tick and stops cleanly, an operator CLI.
- Containers: database, one-shot migrate, api, worker; host ports configurable through `<PREFIX>_PG_HOST_PORT` and `<PREFIX>_API_HOST_PORT` so several projects share one machine.
- `tests/scenarios/` with S0 (the service boots and answers) and `tests/persistence/contracts/` with the contract-suite pattern.
- A deliberate violation of each guard and each layer contract fails `check` (document how to try it in the README).

## Adding a stack

1. Write the profile: `skills/engineering-standards/references/stacks/<name>.md` (contract in that folder's README).
2. Build `scaffolds/<name>/` to this contract; `check` green on a clean machine.
3. `scaffolds/check-contract.sh <name>` passes.
4. CHANGELOG entry; README stacks table row.
