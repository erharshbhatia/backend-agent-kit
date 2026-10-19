# Glossary

<!-- The binding vocabulary. One concept, one name, everywhere: code, tables, docs, UI copy, logs. Add a term the first time it appears in a design doc. When a term is renamed, move the old one to "Retired terms"; the review checklist rejects retired terms as system names. -->

## Terms

| Term | Meaning |
| --- | --- |
| <Term> | <One-sentence definition; where it lives (table, module)> |
| Unit of work | The transaction boundary: repositories run inside it and only it commits |
| Port | A `typing.Protocol` the application depends on; implemented by adapters |
| Adapter | One implementation of a port for one technology |
| Composition root | `bootstrap.py`, the only module that chooses concrete implementations |
| Memory twin | In-memory implementation of a repository port that passes the same contract suite |
| Recorded intent | A row written before an external write, holding the idempotency key and later the outcome |
| Outcome (current) | The deliverable being built now, defined in `implementation/outcome-NN-<slug>.md` |
| Phase | A planned body of work with its own doc (`pNN-*.md`) and ledger (`PNN-*.md`) |
| Change record | The document every change leaves in `docs/changes/` |
| ADR | Architecture decision record in `docs/decisions/` |

## Retired terms

<!-- Words that must not be used as system terms, with the term to use instead. -->

| Retired | Use instead | Why |
| --- | --- | --- |
| <old word> | <term> | <reason / ADR> |
