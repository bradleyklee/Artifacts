---
shot: 18
date: 2026-07-31
status: complete
---

# Inline multiplicities and matrix spacing

The boxed multiplicity labels were removed. Each tree now carries a single plain monospace caption with the multiplicity immediately appended, for example `{1,{1,1}}x75`.

The matrix section was reformatted independently:

- exact matrices use larger display mathematics;
- matrix row height is multiplied by 1.42;
- matrix column spacing is widened;
- fractions are rendered in display style;
- the matrix, rational certificate, telescoping identity, and dimensional check are separated by explicit vertical space.

Fresh files:

- Per case: `release/certificate_WITH_INLINE_MULTIPLICITIES.pdf` and `.tex`.
- Aggregate: `ALL_23_CERTIFICATES_INLINE_MULTIPLICITIES_v7.pdf`.

Checks:

- 23/23 individual PDFs remain one page.
- Zero overfull boxes.
- Aggregate remains 24 pages.
- Exact arithmetic and embedded payload checks remain passing.
- Fraction-heavy q=2/q=3, high-order, and rational-descendant pages were rendered and inspected.

All case states remain verified; there are no blockers.
