# Herfurtner–Miranda classification and model-search artifact

This artifact has one front-to-back purpose:

```text
classify allowable four-fibre configurations
-> search for plane Hamiltonian realizations
-> compute periods
-> search for Laurent models
-> compare with OEIS and record status
-> replay every retained result
```

The order matters.  Classification produces the target set.  The later searches
must read that generated target set rather than begin from a handwritten list.

All commands below are run from the artifact root.

## 1. Reproduce the classification

The classification generator is:

```text
code/classification/generate_configurations.py
```

It starts from the Kodaira fibre table, enumerates every unordered fibre
multiset with Euler sum 12, applies Miranda's numerical conditions
(1.3)–(1.11), and removes the 14 exceptional impossible cases in Table (2.1).

The recovered counts are:

```text
all Euler-sum-12 multisets         379
numerically admissible             293
exceptionally impossible            14
allowable                           279

four-fibre raw slice                 85
four-fibre numerically admissible    69
four-fibre allowable                 59
nonconstant-J Herfurtner targets     56
constant-J four-fibre cases           3
```

Derive the data in memory and compare it with the checked-in ledgers:

```text
python3 code/classification/generate_configurations.py --check
```

Regenerate the ledgers:

```text
python3 code/classification/generate_configurations.py --write
```

Print the complete four-fibre target set:

```text
python3 code/classification/generate_configurations.py \
  --print-set targets
```

The generated files are:

```text
examples/data/configuration_audit_v2.json
examples/data/allowable_configurations_v2.json
examples/data/four_fibre_allowable_v2.json
paper/CONFIGURATION_REPORT.md
```

`configuration_audit_v2.json` records all 379 candidates, every individual
numerical test, every failure, and every exceptional obstruction.

## 2. Inspect the trusted plane-model catalogue

Print the eleven retained plane Hamiltonian models without running a new
coefficient search:

```text
python3 code/run_model_search.py --known-only
```

The Hamiltonian convention is:

```text
alpha = 2 H(p,q)
      = p^2 + q^2 + higher-degree terms.
```

The current trusted catalogue contains eleven plane models covering eleven of
the 56 nonconstant-J four-fibre configurations.

The catalogue is a set of preferred representatives.  Alternate presentations
of the same fibre class belong in the search ledger rather than in the main
one-model-per-class table.

## 3. Run the bounded plane-model search

Run the default bounded search:

```text
python3 code/run_model_search.py
```

This command:

```text
1. prints the trusted eleven-model catalogue;
2. searches integral cubic coefficients in [-3,3];
3. rechecks the eight retained structured-quartic witnesses;
4. groups exact hits by Kodaira fibre configuration;
5. writes the full search record.
```

Use a larger cubic coefficient box explicitly:

```text
python3 code/run_model_search.py \
  --cubic-bound 4 \
  --progress-every 500
```

Progress is printed during every stage.  The final table uses the Kodaira fibre
configuration as its first column and keeps human-readable output within
80 columns.

The complete machine-readable record is:

```text
examples/data/model_search_results.json
```

The current bounded cubic search finds many exact presentations but no new
fibre configurations beyond the trusted catalogue.  Distinct coefficient
tuples or invariant triples are not automatically distinct elliptic surfaces:
base transformations, coordinate changes, and energy rescalings must still be
checked before claiming inequivalence.

## 4. Plane-family coverage

The generated 56-target list is tested against the intended plane families in:

```text
code/plane_scan/
```

The current verified coverage is:

```text
3 cubic configurations
8 structured-quartic configurations
11 total configurations
```

There is no overlap between the retained cubic and quartic rows.

Structural screening is not a coefficient search.  A target marked
`candidate_without_witness` remains open until an exact plane Hamiltonian is
produced and verified.

Auxiliary experiments, including the tacnode search, do not count as coverage
unless they produce a verified model in the intended Hamiltonian class.

## 5. Compute period data

Exact period calculations are stored and replayed through:

```text
code/period_scan/
examples/data/
examples/certificates/
```

The retained baseline has exact period data for all eleven trusted plane
models.

A period record should contain, at minimum:

```text
Hamiltonian
critical values
Kodaira fibre configuration
normalized coefficient sequence
Picard–Fuchs operator
exact certificate or replay data
```

## 6. Search for Laurent models

Laurent searches and certificates are kept in:

```text
code/laurent_search/
examples/certificates/
paper/SEARCH_LEDGER.md
```

A Laurent claim is complete only when the constant-term identity and its exact
recurrence or differential certificate replay successfully.

A failed bounded ansatz is recorded only as a bounded exclusion.  It is never
reported as proof that no Laurent model exists.

The current retained Laurent results include the established baseline cases and
the two cubic models in the same Kodaira class:

```text
A303790
  alpha = p^2 + q^2 + p^3 + q^3

  F(w,y) =
    ((1+w)^3*(1+y)^2*(y^2-4*y+1)^2)/(w^2*y^3)

A295870
  alpha = p^2 + q^2 + p^3 - p*q^2

  F(x,y) =
    ((1+x)^3*(1+y)^2*(1+y^2)^2)/(x*y^3)
```

For A295870,

```text
A295870(n) = [F(x,y)^n]_0
```

follows immediately from the factorization

```text
F(x,y)
  = ((1+x)^3/x)
    * ((1+y+y^2+y^3)^2/y^3).
```

The elementary constant-term proof is complete.  The generic two-variable
G,U,V,J factory also finds an order-two closure, but its full large-matrix
reconstruction is still a performance task.  A factored one-variable
certificate is the preferred completion path.

The detailed A295870 note is:

```text
paper/A295870_LAURENT_RESULT.md
```

## 7. Maintain the research ledger

All status distinctions belong in:

```text
examples/data/research_ledger.json
paper/SEARCH_LEDGER.md
paper/TECHNICAL_LEDGER.md
```

Keep the following states distinct:

```text
verified plane model
alternate plane presentation
verified period
verified Laurent model
bounded Laurent failure
candidate without witness
possible equivalence
proved equivalence
exact OEIS match
no exact-prefix OEIS match located
```

“No exact-prefix match located” is not evidence that a sequence is absent from
OEIS.

## 8. Run the complete release audit

Run:

```text
python3 code/run_release_checks.py
```

The audit order is deliberate:

```text
classification derivation
-> classification regression tests
-> promoted certificate verification
-> legacy certificate verification
-> plane-family coverage
-> period recomputation
-> Laurent verification
-> syntax check
```

Every expensive stage reports progress.  A release is not complete merely
because stored JSON parses; the mathematical certificates and generated data
must replay.

## 9. Main artifact layout

```text
code/classification/
  Derive and audit all allowable fibre combinations.

code/plane_scan/
  Test the generated targets against cubic and quartic plane families.

code/period_scan/
  Recompute exact period data.

code/laurent_search/
  Test Laurent candidates and replay exact certificates.

examples/data/
  Generated classification data, model searches, and research ledgers.

examples/certificates/
  Exact certificates for retained complete cases.

examples/A303790/
examples/A295870/
  Worked cubic examples.

paper/CONFIGURATION_REPORT.md
  Classification counts and the complete 56-target table.

paper/MODEL_TABLE.md
  Preferred plane representatives.

paper/SEARCH_LEDGER.md
  Model, Laurent, failure, equivalence, and OEIS status.

paper/EXPLORATORY_SEARCH_NOTE.md
  Searches that did not enlarge verified coverage.
```

## 10. Reporting rules

```text
1. Classification must precede model search.
2. Use the generated 56-target ledger, not a handwritten replacement.
3. Report one preferred plane representative per fibre class in the main table.
4. Preserve alternate exact presentations in machine-readable ledgers.
5. Do not count a new presentation as a new fibre configuration.
6. Do not count structural candidates as verified models.
7. Do not turn bounded search failure into nonexistence.
8. Do not claim equivalence without an explicit transformation or invariant proof.
9. Print progress during long searches and verification stages.
10. Keep human-readable terminal output within 80 columns.
11. Record successes and failures in JSON.
12. Preserve backward compatibility unless a breaking change is explicit.
