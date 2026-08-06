# Miranda–Herfurtner curve classification and model search

## 1. Purpose

This artifact records a validated curve dataset and replays its exact
Hamiltonian and Laurent certificates. It also contains bounded exploratory
searches for additional plane Hamiltonian presentations.

The public release presents one validated dataset. Discovery history and old
workflow distinctions are kept under `internal/`. The main public operation is
the exact complete-case verifier; catalogue printing is the main inspection
command, while bounded curve search is advanced exploratory use.

## 2. Mathematical input and output

The main input is the generated list of 56 nonconstant-J four-fibre targets.
The Hamiltonian convention is

```text
alpha = 2H(p,q) = p^2 + q^2 + higher-degree terms.
```

For each retained model, the artifact records the fibre classification,
Hamiltonian, arithmetic scale, period operator, Laurent status, exact
coefficients, and OEIS identifier when known.

Rebuild and check the target list with

```text
python3 code/classification/generate_configurations.py --check
```

The recovered counts are

```text
379 Euler-sum-12 multisets
279 allowable configurations
59 allowable four-fibre configurations
56 nonconstant-J targets
3 constant-J cases
```

## 3. Complete cases

Models 1, 2, 3, 5, 7, and 9 have status `complete`.

A complete case passes all of the following exact checks:

```text
Hamiltonian certificate
Laurent certificate
annihilator comparison
recurrence check
initial coefficient check
residual zero
```

The public manifest is

```text
examples/public/complete_cases.json
```

The remaining retained models have exact period data but incomplete Laurent
status.

## 4. Unified verification command

Run all complete cases through one interface:

```text
python3 code/certificates/verify_complete_cases.py
```

The verifier prints each major stage when it starts and passes, including the
model number, elapsed time, and exact failing stage if a check fails. Compact
stage messages avoid wrapped parenthetical details. Every terminal line is at
most 80 columns.

Run the complete release audit with

```text
python3 code/run_release_checks.py
```

## 5. Printed curve catalogue

Print every retained Hamiltonian, sorted by fibre classification and model
number:

```text
python3 code/search_curves.py --print-catalogue
python3 code/search_curves.py --print-catalogue --verbose
```

A normal bounded search also prints the catalogue after the search results.
The checked-in catalogue files are

```text
examples/public/catalogue/CURVES.txt
examples/public/catalogue/curves.json
```

`CURVES.txt` is plain text. `curves.json` retains exact Hamiltonian
coefficients and metadata.

## 6. Incomplete cases

Models 4, 6, 8, 10, and 11 have exact plane models and period data, but their
Laurent completion remains open.

A failed bounded ansatz is recorded only as a bounded exclusion. It is not a
proof that no Laurent model exists. Structural candidates are not counted as
verified plane models until an exact witness is produced.

## 7. Project layout

```text
code/classification/       derive and audit fibre configurations
code/plane_scan/           verify cubic and structured-quartic models
code/period_scan/          recompute exact period data
code/laurent_search/       run and replay Laurent searches
code/certificates/         exact complete-case verification
examples/public/           public manifests and curve catalogue
examples/data/             exact generated data and search records
examples/certificates/     retained certificate data
paper/                     public reports and mathematical tables
internal/                  provenance and development history
```

## 8. Advanced implementation details

The bounded presentation search is

```text
python3 code/search_curves.py
```

Use a larger cubic coefficient box with

```text
python3 code/search_curves.py --cubic-bound 4 --progress-every 500
```

A presentation is one exact coefficient tuple and its plane Hamiltonian. An
invariant model groups presentations having the same stored `c4`, `c6`, and
discriminant. This is the search program's exact deduplication rule; it is not
a claim that differently normalized invariant triples cannot be isomorphic.

The search reads the generated target ledger, rechecks all retained quartic
witnesses, groups exact hits by fibre classification and invariant model,
prints all invariant models, and writes
`examples/data/model_search_results.json`.

Exact verification uses explicit polynomial operations, sparse Laurent
arithmetic, coefficient extraction, and named recurrence transformations.
Generic `simplify` is not used as a proof step. Public and internal data remain
separate, and all machine-readable results are recorded in JSON.
