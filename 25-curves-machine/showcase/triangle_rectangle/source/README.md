# Triangle-Rectangle Genus-One Periods

Final reproducible certificate example for

```text
alpha = 2H(p,q)
      = p^2 + q^2 + (q^3 - 3p^2 q)/2 + (q^2 - 3p^2)^2/16,
0 <= alpha < 1.
```

The project proves and checks the period equation, exact differential
certificate, Abel identity, hypergeometric pullbacks, birational reduction to
a Jacobi quartic and Legendre cubic, and the resulting realization of
Ramanujan's `E4-K^4` identity.

## Final release

```text
release/triangle_rectangle_genus_one_periods_certificate_v5_17_payload.pdf
```

Only the final release PDF is retained in this example folder.

## Verification status

The packaged verifier regenerates and passes 35 proof-level checks.

```bash
python3 -m pip install -r requirements.txt
make verify
make verify-transforms
```

To rebuild the PDF and its embedded autonomous-review payload:

```bash
python3 build.py --regenerate-analysis --regenerate-figure
```

## Main files

- `certificate_source.tex` - visible two-page certificate source.
- `build.py` - verify, compile, attach payload, and update hashes.
- `verify_certificate.py` - exact symbolic and high-precision checks.
- `verify_continued_eisenstein_root.py` - global fourth-root continuation audit.
- `scripts/verify_hypergeometric_transform_chain.py` - exact transformation-chain checks.
- `scripts/generate_quantized_levels.py` - contour-level regeneration.
- `scripts/generate_figure.py` - deterministic figure regeneration.
- `payload/` - files embedded in the release PDF for autonomous review.
- `docs/SOURCES.md` - external source used for Ramanujan's identity.

Generated LaTeX intermediates and historical revision notes are intentionally
excluded from this final example folder.
