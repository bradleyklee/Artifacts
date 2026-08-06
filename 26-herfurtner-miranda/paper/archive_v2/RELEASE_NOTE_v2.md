# Miranda-Herfurtner plane Hamiltonian release v2

## Purpose

This package keeps two searches on equal footing: discovering useful elliptic
plane models and discovering Laurent polynomials for their periods. Every
positive result, bounded failure, and OEIS check has a machine-readable record.

## Results carried forward

- 11 exact baseline plane models among the historical 56 nonconstant-J
  four-fiber configurations.
- Exact period data for all 11.
- Exact Laurent certificates for baseline models 1, 2, 3, 5, 7, and 9.
- A complete worked A303790 example.

## New curve results

A one-tacnode harmonic quartic family was solved explicitly. Generic members
have the already-known fiber configuration `III*+I1+I1+I1`, so this round adds
plane presentations rather than a new Herfurtner configuration.

The special model

```text
2H=p^2+q^2+q^3-q^4/4
```

has exactly the same normalized period as baseline model 1. Its Laurent
certificate is therefore already complete by transfer.

The sheared model

```text
2H=p^2+q^2+2p^2q+q^3+p^2q^2-q^4/4
```

has the new scale-32 period

```text
1, 76, 12084, 2361680, 509004580, 116126173296, ...
```

and a checked third-order equation. Its Laurent model is open.

## New Laurent-search results

For baseline models 4, 8, and 10, the degree-5 and degree-6 integer
palindromic product search is now exhausted exactly. More than 53 million
square-vector cases were covered; some match three reduced moments, but none
matches the fourth. A separate 495-support rank-two box has also been excluded.

The correct next move is not degree 7 in the same one-dimensional pattern. It
is a support change: larger rank-two supports, nonsymmetric supports, mutation
templates, and a separate order-three diagonal search for T1.

## OEIS ledger

Model 2 is the exact OEIS sequence A303790. No exact-prefix match was located
for the other raw stored sequences or T1 in the searches made on 2026-08-05.
The ledger deliberately calls these search outcomes, not proofs of absence.

## Run and layout

All examples are organized directly under `examples/`. Run:

```text
python code/run_release_checks.py
```

Read `paper/SEARCH_LEDGER.md` for the concise status table and
`examples/data/research_ledger.json` for the machine-readable source of truth.
