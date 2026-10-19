# Outcome <NN>: <short name>

| | |
| --- | --- |
| Status | Active — the current build target · Done · Superseded by outcome <NN+1> |
| Owner | <project owner> |
| Decided | YYYY-MM-DD |
| Governs | Which parts of P00–P<NN> are built now and in what order. The phase docs stay the design; this doc says what is **in** for this outcome and what is **deferred** |
| Decisions | ADR-NNNN (<title>), … |

## 1. Outcome

> <One sentence, in the user's words, of what they can do when this is done.>

What gets built for it, and only as much of each as the outcome needs:

1. **<Part>:** <slice>
2. **<Part>:** <slice>

<What is real and what is mocked.>

## 2. What "done" looks like

### 2.1 Demo (manual)

1. <command or action> → <what you see>
2.

### 2.2 Acceptance scenarios (automated)

| ID | Scenario | Proves |
| --- | --- | --- |
| S1 | | <requirement IDs> |

### 2.3 Exit criteria

- All scenarios in §2.2 pass (<N runs in a row if any step is non-deterministic>).
- The §2.1 demo works end to end.
- `make check` green.
- <genericity or quality criterion, e.g. no tenant-specific code in the core package>

## 3. Scope

### 3.1 In

- <item>

### 3.2 Deferred (not in this outcome)

| Item | Phase | Picked up by |
| --- | --- | --- |
| | | outcome <NN+1> / later |

## 4. Build order

Each milestone ends with something you can run. Phase docs hold the design; the slice column says what to build from each.

| Milestone | Phases | Slice | You can then… |
| --- | --- | --- | --- |
| **M1 <name>** | P00 → P01 | <tasks / features from each> | <runnable result> |
| **M2 <name>** | P02 ∥ P03 | | |

<Which phases can run in parallel, and what each parallel pair must agree first (shared ports or models).>

## 5. Decisions

**Made for this outcome (YYYY-MM-DD, owner):**

| Decision | Record |
| --- | --- |
| | ADR-NNNN |

**Still open:** every other item in `docs/workstreams/OPEN-DECISIONS.md`. Only those for the phase being started block it.

## 6. Tracking

Progress is in `docs/workstreams/STATUS.md` (milestone column) and each phase ledger. Tasks outside this outcome's slice are recorded as `not started (deferred: outcome <NN>)`.
