# Final code index

## Certificate pipeline

- `build.py` - runs verification, compiles the certificate, embeds the review
  payload, and updates SHA-256 manifests.
- `certificate_source.tex` - complete visible two-page source.
- `scripts/attach_payload.py` - embeds the autonomous-review files.
- `scripts/update_manifest.py` - updates payload and project hashes.
- `release/triangle_rectangle_genus_one_periods_certificate_v5_17_payload.pdf`
  - final certificate.

## Mathematical verification

- `verify_certificate.py` - 35 exact and high-precision proof-level checks.
- `verify_continued_eisenstein_root.py` - branch-continuation checks.
- `scripts/verify_hypergeometric_transform_chain.py` - exact checks of the
  signature-four, Legendre, and modular pullbacks.
- `analysis/hypergeometric_transform_chain.json` - saved exact residuals and
  transformation data.

## Generated geometry

- `scripts/generate_quantized_levels.py` - action-level table generation.
- `scripts/generate_figure.py` - real and Abel-Wick contours and period graph.
- `assets/geometry_period.pdf` - combined figure used by LaTeX.
- `assets/geometry_left.png`, `assets/geometry_right.png` - component renders.

## Embedded review payload

The `payload/` directory contains the source, executable checks, generated
results, claim index, figure reconstruction data, and SHA-256 manifest that
are attached to the release PDF.
