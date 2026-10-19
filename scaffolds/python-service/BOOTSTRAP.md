# Bootstrapping the python-service scaffold into a project

Copy `scaffolds/python-service/` to the project root (P00-T2), then rename. The scaffold is literally named `app`.

| In the scaffold | Rename to |
| --- | --- |
| directory `app/` and `app/src/app/` | `<package>/` and `<package>/src/<package>/` |
| `app.` in imports, `.importlinter`, `pyproject.toml`, `alembic.ini`, `scripts/guards.toml`, `Dockerfile`, `docker-compose.yml` | `<package>.` |
| `APP_` env prefix in `settings.py`, `.env.example`, `docker-compose.yml` | `<PREFIX>_` |
| `appctl` console script | your CLI name |
| schema `app` in `tables.py` and `0001_baseline.py` | your schema name |
| `app-workspace`, compose project `app`, image `app-python:local` | project names |
| `<Project>` in `pyproject.toml` descriptions, `api.py`, `cli.py` | the project name |

Then fill `scripts/guards.toml` `forbidden_words` with the project's domain words, and add one `.importlinter` contract per vendor SDK that goes behind a port.

Proof the renames are done:

```bash
grep -rn '\bapp\b\|APP_\|appctl\|<Project>' <package> scripts tests *.toml *.yml Dockerfile Makefile .importlinter alembic.ini
```

Only intended hits may remain. Then `uv sync` (creates `uv.lock`; commit it with the code) and `make check`.

Copy `STACK.md` from this folder to `.claude/skills/project-guide/knowledge/STACK.md` and replace `app` / `APP_` there too.
