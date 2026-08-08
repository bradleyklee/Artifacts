# Q2 order-6 exact certificate drill

Start with `Q2_ORDER6_DRILL_REPORT_2026-08-02.md`.

## Main machine-readable artifacts

- `data/q2_operator_exact.json`: normalized rational order-6 operator reconstructed by CRT.
- `data/q2_operator_exact_verified.json`: primitive integer operator and exact-series verification summary.
- `data/q2_primitive_certificate_shift.json`: complete exact primitive and certificate.
- `data/squarefree_alpha_degree_bounds.json`: safe signed-minor alpha-degree bounds.

## Verify the final exact differential identity

From this directory:

```bash
python scripts/verify_q2_certificate_from_json.py \
  --model data/q2_generic.json \
  --src src \
  --operator-verified data/q2_operator_exact_verified.json \
  --certificate data/q2_primitive_certificate_shift.json
```

The full sparse verification takes a few minutes on one core.  Expected status:

```text
EXACT_SPARSE_IDENTITY_PASS
```

## Regenerate the primitive

```bash
python scripts/q2_primitive_shift_recurrence.py \
  --model data/q2_generic.json \
  --src src \
  --operator-verified data/q2_operator_exact_verified.json \
  --output /tmp/q2_primitive_certificate.json \
  --shift 7 --prime 65521 --max-degree 80
```

Expected high-level results:

```text
RECTANGULAR_CHECK_PASS
SPARSE_VERIFY_PASS
primitive alpha degree = 32
primitive expanded terms = 3736
```

## Recompute safe degree bounds

```bash
python scripts/derive_squarefree_alpha_degree_bound.py \
  --max-order 9 --output /tmp/squarefree_alpha_degree_bounds.json
```

At order 6 the uniform safe projective degree bound is 298.

## Dependencies

Python 3, SymPy, and NumPy.
