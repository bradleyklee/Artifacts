# Herfurtner-Miranda classification and model-search release v3

## Purpose of this repair

Release v2 began its plane scan from a checked-in 56-target JSON file without
shipping the code that derived that target list.  It also required pytest even
though the release checks were intended to run in a plain Python environment.

Release v3 repairs those two problems.  It does not claim a new curve model or
a new Laurent polynomial.

## Classification is now stage one

`code/classification/generate_configurations.py` reconstructs the Miranda/Persson
configuration database before any model search:

```text
379 Euler-sum-12 multisets
293 numerically admissible
14 additional exceptional impossibilities
279 allowable configurations
```

Its four-fibre slice is:

```text
85 raw
69 numerically admissible
59 allowable
56 nonconstant-J Herfurtner targets
3 constant-J cases
```

The generator reproduces the recovered full audit exactly, including every
per-configuration test and exceptional obstruction.

## Downstream searches

`code/plane_scan/run_scan.py` now explicitly consumes the generated four-fibre
ledger.  The verified coverage is unchanged:

```text
3 cubic configurations
8 structured two-node quartic configurations
11 total, no overlap
45 targets not realized by these two implemented classes
```

The exact period and Laurent results are also unchanged.  Six of the eleven
baseline models have exact Laurent certificates: 1, 2, 3, 5, 7, and 9.

The tacnode calculation from v2 is retained as an auxiliary experiment only.
It is not part of the default pipeline or evidence that the intended quartic
coefficient search found a new model.

## Reproducibility

Run:

```text
python3 code/run_release_checks.py
```

The audit now uses standard-library `unittest`; pytest is not required.
