# Public walkthrough

This walkthrough recomputes the two primary public examples and then shows how
to enter a new Laurent polynomial.

## 1. Check the installation

```text
python3 code/example.py list --scope public
pytest -q code/tests code/test_00_order4_joint.py
```

## 2. Recompute A295870

```text
mkdir -p results/public
python3 code/example.py certify A295870 \
  --output results/public/A295870.json
```

A successful run ends with `Certificate complete` and reports PASS for the
exact G,U,V,J identity, divergence identity, and recurrence replay.  Operator
discovery methods are reported as `used` or `not used`, not PASS or FAIL.

The input is

```text
((1+x)^3/x)*((1+y+y^2+y^3)^2/y^3)
```

The code expands this as a Laurent polynomial.  It does not require the product
factorization for correctness, although the constant-term engine detects exact
separability when it is available and uses two one-variable convolutions.

## 3. Recompute A303790

```text
python3 code/example.py certify A303790 \
  --output results/public/A303790.json
```

The stored A303790-specific replays can also be run directly:

```text
python3 code/a303790/verify_scalar_certificate.py
python3 code/a303790/derive_and_verify_laurent.py
```

The general `certify` command is the colleague-facing route.  The two shorter
scripts remain as independent checks for the worked paper example.

## 4. Enter another example

```text
python3 code/example.py derive \
  --F "x + y + 1/(x*y) + y^2" \
  --output results/public/order4_triangle.json
```

The parser renames up to two input variables internally.  Coefficients must be
exact.  Write `1/3`, not a decimal approximation.

## 5. Inspect the JSON result

The human report is intentionally short.  The JSON file contains the operator,
constant terms, recurrence, basis data, matrix dimensions, witness layers, and
all exact checks.

```text
python3 -m json.tool results/public/A295870.json | less
```


## Replay every public canonical example

Replay the eleven stored catalogue records only:

```text
python3 code/run_examples.py public
```

Replay those records and recompute every distinct canonical public Laurent
model through the general G,U,V,J solver:

```text
python3 code/run_examples.py public --derive-guvj
```

The full command writes new certificates below
`results/public/canonical/`.  It does not run the perturbation search.

## 6. Reproduce the known failure

The unresolved perturbation is

```text
x + y + 1/(x*y) + y/x^2
```

Its operator is found, but the certificate reconstruction can exceed the
60-second perturbation budget.  Treat a timeout as an unfinished computation,
not as evidence that no certificate exists.
