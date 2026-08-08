# Reproducible certificate source-bundle standard

Every release PDF with a generated curve figure embeds the same 13-file review bundle:

1. `README_AUTONOMOUS_REVIEW.txt` - extraction and replay instructions;
2. `certificate_payload.json` - exact mathematical data and normalization choices;
3. `certificate_source.tex` - exact visible LaTeX source;
4. `claim_index.json` - visible rows mapped to named executable checks;
5. `generate_figure.py` - deterministic figure reconstruction;
6. `generate_quantized_levels.py` - contour-level reconstruction and audit;
7. `quantization_spec.json` - explicit action-level convention and branch orientation;
8. `quantized_levels_for_figure.csv` - checked numerical contour levels;
9. `verification_output.txt` - saved successful replay transcript;
10. `verification_results.json` - machine-readable named check results;
11. `verify_certificate.py` - autonomous proof verifier;
12. `SOURCE_BUNDLE_STANDARD.md` - this convention;
13. `MANIFEST.sha256` - hashes of the other twelve attachments.

## Curve-level convention

For `L` displayed ovals use midpoint normalized-action fractions

    f_n = (n + 1/2) / L,    n = 0, ..., L-1.

For one degree of freedom, `I(E)=Area(C_E)/(2*pi)`.  Only the real branch is normalized
by the action of its bounding separatrix.  Midpoints avoid both the degenerate
center and the separatrix itself.  These are reproducible display/semiclassical
levels; they are not asserted to be an exact quantum spectrum without an
additional choice of `hbar` and Maslov convention.

## Clean extraction test

From the extracted PDF attachments run:

    python3 verify_certificate.py
    python3 generate_quantized_levels.py --check
    sha256sum -c MANIFEST.sha256
    python3 generate_figure.py

The final command rebuilds `assets/geometry_period.png` and
`assets/geometry_period.pdf` using only embedded files.
