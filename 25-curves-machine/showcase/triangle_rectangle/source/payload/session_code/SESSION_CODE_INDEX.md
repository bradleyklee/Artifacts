# Session code index

This folder consolidates the code and outputs developed for the
triangle-rectangle genus-one example.

## Certificate pipeline

- `build.py` - verifies the mathematics, compiles the two-page LaTeX
  certificate, and embeds the autonomous-review payload.
- `certificate_source.tex` - complete two-page certificate source.
- `scripts/generate_figure.py` - code-generated real and Abel-Wick contour
  families and period plot; no image-generation model is used.
- `scripts/attach_payload.py` - embeds the review payload in the release PDF.
- `scripts/update_manifest.py` - regenerates project and payload SHA-256
  manifests.
- `payload/verify_certificate.py` - exact symbolic and high-precision checks
  for the plane certificate, ODE, periods, Abel identity, elliptic
  normalization, Jacobi-Legendre map, modular pullback, and Ramanujan map.

## General-family derivation

- `scripts/derive_general_mu_picard_fuchs.py` - derives the generic
  Picard-Fuchs operator for
  `p^2+q^2+(q^3-3p^2q)+mu*(q^2-3p^2)^2`, proves an exact differential
  certificate, and specializes to `mu=1/4`.
- `analysis/general_mu_picard_fuchs.json` - expanded and factored symbolic
  output from that derivation.

## Hypergeometric transformation chain

- `scripts/verify_hypergeometric_transform_chain.py` - exact pullback checks
  for the `(1/4,3/4)` signature-four form and the `(1/12,5/12)` modular
  `j`-line form.
- `analysis/hypergeometric_transform_chain.json` - formulas and zero
  residuals from those checks.

## Generated assets and release

- `assets/geometry_left.png` - real and interior Abel-Wick contour families.
- `assets/geometry_right.png` - normalized period plot.
- `assets/geometry_period.pdf` - combined code-generated figure included by
  LaTeX.
- `release/triangle_rectangle_genus_one_periods_certificate_v4_payload.pdf`
  - release certificate with embedded payload.
