# Semi-random quartic search packet

Start with `SEARCH_REPORT.md` and `index.json`.

Primary exact results:

- `data/q1e_exhaustive_certificate.json`
- `data/q1b_exact_backsolve.json`

Primary asymmetric modular results:

- `data/q2_holdout_65521.json`
- `data/q2_holdout_65497.json`
- `data/q2_modred_o6_65521_a7.json`
- `data/q2_modred_o6_65497_a11.json`

Replay the compact checks with:

```bash
cd src
python verify_bundle.py
```

The packet deliberately retains failed and bounded search logs.  In particular,
the first Q1 order-6 result is preserved but corrected: the minimal discovered
operator is order 4.
