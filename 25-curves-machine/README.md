# Curves Machine Factory

Research owner: Bradley Klee. Unpublished research; **NO POACHING**.

This repository is the working factory for exact and experimental period calculations on plane and sphere curves. It is intended to be foundational technology: new calculations should enter as examples, remain reproducible, and become human-readable showcase certificates only after they are ready.

## Working rule

`examples/` is the scientific record. Every filed example has a stable case ID, one or more coordinate representations, retained result data, source-path provenance, and a replay entry point. Code names are acceptable. A better human name changes the slug or display name, not the stable ID.

`code/` contains current reusable implementations and comparison code. Case-specific runners may remain beside an example when that is the safest way to preserve a working calculation.

`pseudo/` contains the current language-neutral algorithm descriptions. Code and pseudocode are kept together in the catalog: a new example should not be filed without identifying the code and pseudocode needed to rerun it.

`showcase/` contains only the best human-readable certificate projects. The machine data remains under `examples/`.

`paper/` is reserved for the project paper and references. The supplied source snapshot did not contain the desired project `note.pdf`, so no unrelated PDF has been renamed as the note.

## Basic commands

```bash
python3 code/tools/list_cases.py
python3 code/tools/verify_factory.py
python3 code/tools/run_case.py S0003
python3 code/tools/run_case.py P0007 --full
```

Each case also has `scripts/reproduce.py`, so it can be replayed directly from its own README.

## Data lifecycle

- `representations/` describes coordinate realizations of the same mathematical case.
- `transforms/` records exact maps between representations when available.
- `runs/` preserves imported or newly generated run state.
- `results/` contains the filed result objects.
- `certificates/machine/` contains exact proof objects and verification output.
- `showcase/<name>/certificate.pdf` is the current human-facing certificate.

Raw or failed calculations are not discarded. Promotion to `showcase/` does not move or replace the corresponding example.

## Migration boundary

This factory was built from `25-curves-machine(1).zip`. The input archive hash and per-file disposition ledger are retained at the repository root. Historical branch snapshots, obsolete PDF revisions, caches, and duplicate merger scaffolding were not copied into the active tree.
