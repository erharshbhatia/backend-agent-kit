# Stack

<!-- Fill-in template. `project-bootstrap` copies the chosen scaffold's STACK.md here (scaffolds/<name>/STACK.md). The skills never name a concrete tool; they say `check`, `deps-sync`, "the composition root", and this file says what that is for this project. Keep it true: a changed command or tool is a `config` change that updates this file. -->

| | |
| --- | --- |
| Profile | <name from `engineering-standards/references/stacks/`, e.g. python-postgres> |
| Stack ADR | ADR-0002 |
| Package root | <path, e.g. `herald/src/herald/`> |
| Env prefix | <PREFIX>_ |

## Commands

| Abstract name | Concrete command | Needs |
| --- | --- | --- |
| `check` | <all gates: lint, format, types, layer contracts, guards, fast tests> | nothing |
| `check-all` | <check + database tests + migrations check> | Docker |
| `test` | <fast tests only> | nothing |
| `test-db` | <tests tagged `db`> | Docker |
| `test-external` | <tests tagged `external`> | keys, owner's go-ahead |
| `e2e` | <end-to-end scenarios> | Docker if scenarios use the database |
| `migrations-check` | <schema source of truth and migrations agree> | a migrated database |
| `deps-sync` | <install dependencies from the lock file> | network |
| `deps-lock` | <regenerate the lock file> | network |
| `up` / `migrate` / `stack` / `down` | <local database only / apply migrations / whole system in containers / stop> | Docker |
| <project's own> | <e.g. eval, ui-check> | |

## Tools

| Role | Tool | Config |
| --- | --- | --- |
| Linter and formatter | | |
| Type checker (strictest mode) | | |
| Layer-contract tool | | |
| Banned-API tool (wall clock, random ids, environment reads) | | |
| Domain-word, SQL-location, repository guards | | |
| Test runner, property testing, test containers | | |
| Migration tool | | |

## Files behind the abstract names

| Abstract name | File |
| --- | --- |
| Composition root | |
| Settings module | |
| Dependency manifest | |
| Lock file | |
| Schema source of truth | |
| Persistence adapter package (the only SQL) | |
| Memory twins package | |
| Contract-suite directory | |
| Env example file | |

## Store primitives

| Need | This stack |
| --- | --- |
| Atomic claim of queued work | <e.g. `FOR UPDATE SKIP LOCKED`> |
| Idempotent insert | <e.g. `INSERT … ON CONFLICT DO NOTHING RETURNING`> |
| Wake-up for workers | <e.g. LISTEN/NOTIFY, or polling> |
| Time-ordered unique ids | <e.g. UUIDv7> |
