# backend-agent-kit: rules for working on the kit itself

This repository is the plugin, not a project built with it. `templates/CLAUDE.md` is what a project gets.

## Always

1. **Generic stays generic.** Nothing under `skills/` names a project, a package, an env prefix, a vendor, or a concrete tool or command. Skills use the abstract names of `templates/project-guide/knowledge/STACK.md` (`check`, `deps-sync`, "the composition root", "the atomic claim primitive"). Stack specifics go in `skills/engineering-standards/references/stacks/<profile>.md` and `scaffolds/<name>/`.
2. **One canonical copy.** The shared-hot-files list lives in `workstream-tracking`; the audit recipe in `sdlc-workflow`; the isolation modes in `multi-agent-development`. Other skills link, never copy.
3. **Templates match skills.** A change to a skill that changes what a project must contain (a new ledger file, a new knowledge file, a new target) updates `templates/`, `scaffolds/CONTRACT.md`, every scaffold, and `CHANGELOG.md` with a "Project side" line, in the same change.
4. **Verify before claiming.** `claude plugin validate .` (the one accepted warning is the root `CLAUDE.md`, which is this file, for people and sessions working on the kit, not plugin context), `scaffolds/check-contract.sh <name>` for every scaffold, and `make check` inside each scaffold must be green; paste the output in the commit message body or the PR.
5. **Descriptions trigger.** Every `SKILL.md` description says what the skill is and when to use it, in the third person, under 1024 characters.
6. **Workflows stay generic.** `workflows/*.js` read everything from `args` (repo, scratch, isolation, stack commands, agent type names, tasks) and touch no repository files; the coordinator integrates. Keep `WORKER_REPORT` in `wave.js` identical to `skills/multi-agent-development/references/worker-report-schema.json`.
7. **Bump and log.** A user-visible change bumps `version` in both manifests and adds a `CHANGELOG.md` entry, newest first.

## Never

- Put `<Project>`, `<package>`, `<PREFIX>`, `<domain-words>` or `<vendor>` placeholders in `skills/`; they belong in `templates/` and scaffold `BOOTSTRAP.md` files only.
- Use em-dashes in prose; tables and short sentences instead.
- Report checks as passing without having run them.
- Commit or push unless the owner asks.
