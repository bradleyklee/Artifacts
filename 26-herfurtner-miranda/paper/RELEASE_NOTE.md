# Miranda–Herfurtner release report

## Release status

The artifact contains 11 retained plane Hamiltonian models covering 11 of the
56 nonconstant-J four-fibre targets.

Six models are complete:

```text
1, 2, 3, 5, 7, 9
```

Five models remain incomplete on the Laurent side:

```text
4, 6, 8, 10, 11
```

## Exact verification

Run

```text
python3 code/certificates/verify_complete_cases.py
```

Every complete case is checked through the same public interface for

```text
exact Hamiltonian certificate
exact Laurent certificate
matching annihilator
matching recurrence
matching initial terms
exact residual zero
```

The verifier uses exact arithmetic and prints readable progress throughout.

## Curve catalogue

Run

```text
python3 search_curves.py --print-catalogue
```

The public catalogue is also stored in

```text
examples/public/catalogue/CURVES.txt
examples/public/catalogue/curves.json
```

The text file prints every retained Hamiltonian with its fibre classification,
scale, and final status. The JSON file retains exact coefficients and metadata.

## Classification and coverage

The classification generator recovers

```text
379 Euler-sum-12 multisets
279 allowable configurations
59 allowable four-fibre configurations
56 nonconstant-J targets
3 constant-J cases
```

The implemented plane families cover

```text
3 harmonic cubic configurations
8 structured-quartic configurations
11 total configurations
```

Bounded failures remain bounded exclusions only.

## Reproducibility

Run the complete audit with

```text
python3 code/run_release_checks.py
```
