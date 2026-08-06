# Herfurtner-Miranda classification and model-search artifact v3

This artifact has a strict front-to-back pipeline.  It does **not** begin with
an unexplained list of 56 targets.

## Curve-model catalog and bounded search

Print the trusted eleven-model catalog:

```bash
python3 code/run_model_search.py --known-only
```

Print the catalog, search integral cubic coefficients in `[-3,3]`,
and recheck the eight retained structured-quartic witnesses:

```bash
python3 code/run_model_search.py
```

Progress is printed during every search stage.  The final table uses the
Kodaira fiber code as its first column and stays within 80 columns.  Exact
search records are written to:

```text
examples/data/model_search_results.json
```

A larger cubic box can be selected explicitly:

```bash
python3 code/run_model_search.py --cubic-bound 4 --progress-every 500
```

The bounded search lists exact invariant models.  It does not yet prove
that different invariant triples are inequivalent under every allowed
base or coordinate transformation.

## 1. Derive the valid fibre combinations

The first stage is:

```text
code/classification/generate_configurations.py
```

It uses only the Python standard library.  Starting from the ordered Kodaira
fibre table, it enumerates every unordered fibre multiset with Euler sum 12,
applies Miranda's numerical conditions (1.3)--(1.11), and then removes the 14
exceptional impossible cases from Table (2.1).

The recovered counts are:

```text
all Euler-sum-12 multisets      379
numerically admissible          293
exceptionally impossible         14
allowable                        279

four-fibre raw slice              85
four-fibre numerically admissible 69
four-fibre allowable              59
nonconstant-J Herfurtner targets  56
constant-J four-fibre cases        3
```

The three generated ledgers are:

```text
examples/data/configuration_audit_v2.json
examples/data/allowable_configurations_v2.json
examples/data/four_fibre_allowable_v2.json
```

`configuration_audit_v2.json` records every one of the 379 candidates, every
individual test, every failure, and each exceptional obstruction.  The compact
report is `paper/CONFIGURATION_REPORT.md`.

To regenerate the database:

```text
python3 code/classification/generate_configurations.py --write
```

To derive it in memory and require exact equality with the checked-in ledgers:

```text
python3 code/classification/generate_configurations.py --check
```

## 2. Search for plane Hamiltonian realizations

Only after classification does the artifact search the intended families

```text
alpha = 2 H(p,q) = p^2 + q^2 + cubic terms + quartic terms.
```

`code/plane_scan/run_scan.py` reads the **generated** four-fibre ledger, removes
the three constant-J cases, and tests the resulting 56 targets against:

1. `harmonic_plus_cubic`;
2. `two_node_structured_quartic`.

The current verified coverage remains 3 cubic plus 8 quartic configurations,
with no overlap.  Structural screening is not a coefficient search: a target
marked `candidate_without_witness` is still open.

## 3. Compute periods and search for Laurent models

The period and Laurent tracks are independent of the plane-model coverage:

```text
code/period_scan/
code/laurent_search/
```

The retained baseline has exact period data for all 11 plane models and exact
Laurent certificates for models 1, 2, 3, 5, 7, and 9.  A failed bounded Laurent
ansatz is recorded as a bounded exclusion, never as nonexistence.

## 4. OEIS and research ledger

Model status, Laurent status, equivalence status, failed searches, and OEIS
status belong in:

```text
examples/data/research_ledger.json
paper/SEARCH_LEDGER.md
```

OEIS entries must distinguish an exact match from “no exact-prefix match
located”; the latter is not a proof that the sequence is absent from OEIS.

## Run the release audit

The release audit uses the standard library test runner and does not require
pytest:

```text
python3 code/run_release_checks.py
```

Its order is deliberate:

```text
classification derivation
-> certificate verification
-> plane-family coverage
-> period recomputation
-> Laurent-search verification
-> syntax check
```

The tacnode experiment retained from v2 is auxiliary and is not part of this
default pipeline or the intended quartic coefficient search.

## Main layout

- `code/classification/`: derive and audit all allowable fibre combinations.
- `code/plane_scan/`: test generated targets against the cubic and quartic families.
- `code/period_scan/`: exact period calculations.
- `code/laurent_search/`: Laurent candidates, bounded searches, and certificates.
- `examples/data/`: generated classification data and research ledgers.
- `examples/certificates/`: exact certificates for the complete baseline cases.
- `paper/CONFIGURATION_REPORT.md`: the classification counts and 56-target table.
- `paper/SEARCH_LEDGER.md`: model, Laurent, failure, equivalence, and OEIS status.
