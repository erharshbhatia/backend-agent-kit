# Stack profiles

The generic files in `engineering-standards` name abstract things: `check`, the layer-contract tool, the composition root, the persistence adapter package. A **profile** says what those are for one language and database, with the code shapes and the tools that enforce the rules. A project uses exactly one profile, chosen by its stack ADR at bootstrap (`project-bootstrap`); bootstrap copies the profile's stack table into `project-guide/knowledge/STACK.md`.

Profiles today:

| Profile | Language | Database | Scaffold |
| --- | --- | --- | --- |
| `python-postgres.md` | Python 3.12 | PostgreSQL 16 | `scaffolds/python-service/` |

## What a profile must contain

Same section order in every profile, so a reader can switch stacks without relearning the document.

| # | Section | Must answer |
| --- | --- | --- |
| 1 | Stack table | One row per abstract name used by the generic files: the commands (`check`, `check-all`, `test`, `test-db`, `test-external`, `e2e`, `migrations-check`, `deps-sync`, `deps-lock`), the tools (linter/formatter, type checker, layer-contract tool, banned-API tool, the three guards), the files and roles (package root, composition root, settings module, dependency manifest, lock file, schema source of truth, migration tool, persistence adapter package, memory twins package, contract-suite directory). This table is what `STACK.md` holds |
| 2 | Layout | The package tree the scaffold ships, with the role of each directory |
| 3 | Idioms | One subsection per `clean-code.md` section (1 to 9): how the convention is spelled in this language, which library or tool, which setting |
| 4 | Repository implementation | The unit of work and one example repository port with code; the schema source of truth; the atomic claim primitive; idempotent insert; wake-ups if the store has them; the migration check |
| 5 | Testing | The tools per pyramid row; how the two reserved tags `db` and `external` are declared and enforced; the frozen clock and seeded ids; the contract-suite fixture shape; the concrete commands |
| 6 | Enforcement map | Which tool enforces each of the ten rules and each of R1 to R15, with the configuration file it lives in |
| 7 | Scaffold | Where it is, what it ships, how it is renamed for a project |

Rules: a profile adds nothing to the ten rules or R1 to R15; it only says how they are met. Anything that holds for every language belongs in the generic file, not in a profile.

## Adding a profile

1. Copy `python-postgres.md` to `<language>-<database>.md` and rewrite every section for the new stack, keeping the order above.
2. Build the matching scaffold under `scaffolds/<name>/` so that the stack table's commands exist and `check` is green on a clean machine; the scaffold must ship a `Clock`, an `IdGenerator`, the unit-of-work port with a memory twin, the three guards, and the scenarios directory with S0.
3. Add the row to the table above and to `project-bootstrap`'s stack choice.
4. Record it in the kit's `CHANGELOG.md`.
