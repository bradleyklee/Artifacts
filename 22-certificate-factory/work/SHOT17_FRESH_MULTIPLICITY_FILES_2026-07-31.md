---
shot: 17
date: 2026-07-31
status: complete
---

# Fresh multiplicity-labelled files

Every tree figure now has a bordered red label reading `MULTIPLICITY × N`, including multiplicity one. The label is placed on its own line immediately beneath the tree and above the brace code.

Fresh filenames prevent PDF/browser caches from resolving to an older file:

- Per case: `release/certificate_WITH_MULTIPLICITIES.pdf` and matching `.tex`.
- Aggregate: `ALL_23_CERTIFICATES_WITH_MULTIPLICITIES_v6.pdf`.

Legacy certificate names are retained as aliases to the fresh files.

Checks:

- A120590 visibly renders four `MULTIPLICITY × 1` labels.
- A120607 visibly renders `× 3`, `× 15`, `× 75`, and `× 120`.
- All 23 individual PDFs remain one page.
- Aggregate remains 24 pages.
- Zero overfull boxes.
- Arithmetic and embedded-payload audit passes all 23 cases.

All case states remain verified; no blockers remain.
