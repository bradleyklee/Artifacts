# Reproducible certificate source-bundle standard

Every final release PDF embeds the following 18-file autonomous-review bundle:

1. `MANIFEST.sha256` - hashes of the other seventeen attachments;
2. `README_AUTONOMOUS_REVIEW.txt` - extraction and replay instructions;
3. `certificate_payload.json` - exact mathematical data and normalization choices;
4. `certificate_source.tex` - exact visible LaTeX source;
5. `quantized_levels_for_figure.csv` - checked contour levels;
6. `verification_output.txt` - saved successful replay transcript;
7. `verification_results.json` - machine-readable named check results;
8. `continued_eisenstein_root_check.json` - global branch audit;
9. `continued_eisenstein_root_check.csv` - tabular global branch audit;
10. `solution_basis_audit.json` - global solution-basis audit;
11. `solution_basis_audit.csv` - tabular global solution-basis audit;
12. `claim_index.json` - visible rows mapped to executable checks;
13. `verify_certificate.py` - autonomous proof verifier;
14. `verify_continued_eisenstein_root.py` - branch-continuation verifier;
15. `generate_figure.py` - deterministic figure reconstruction;
16. `generate_quantized_levels.py` - contour-level reconstruction;
17. `quantization_spec.json` - action-level convention and branch orientation;
18. `SOURCE_BUNDLE_STANDARD.md` - this convention.

## Curve-level convention

For `L` displayed ovals use midpoint normalized-action fractions

```text
f_n = (n + 1/2) / L,    n = 0, ..., L-1.
```

For one degree of freedom, `I(E)=Area(C_E)/(2*pi)`. Only the real branch is
normalized by the action of its bounding separatrix. Midpoints avoid both the
degenerate center and the separatrix itself. These are reproducible display
and semiclassical levels; they are not asserted to be an exact quantum
spectrum without an additional choice of `hbar` and Maslov convention.

## Clean extraction test

From the extracted PDF attachments run:

```bash
python3 verify_certificate.py
python3 generate_quantized_levels.py --check
sha256sum -c MANIFEST.sha256
python3 generate_figure.py
```

The final command rebuilds `assets/geometry_period.png` and
`assets/geometry_period.pdf` using only embedded files.
