---
shot: 20
date: 2026-07-31
scope: certificate presentation only
status: complete
time_limit: 15 minutes
---

# Author, matrix-tuple, footer, and A120589 pass

## Changed

- Replaced `Harm.On.ica S-O-L 5.6 (OpenAI)` with `Mech.An.ika Sol` on all
  certificate author lines and on the aggregate cover.
- Added `Compare with the verbose certificate for A120590.` to every footer.
- Enforced coherent matrix presentation: a page shows `G,U,V,J`, `U,V,J`, or
  no matrices. Cases without a complete compact tuple now direct the reader to
  embedded exact reduction data without naming a partial tuple.
- Corrected A120589 to display
  `A(x)=A_parent(x)^2, A_parent(x)=A_120588(x)` with proper mathematical
  subscripts and italics.
- Hardened PDF generation against transient short writes by validating a
  staged PDF and atomically publishing it.

## Checks and case states

- 23/23 cases remain verified and certificate-ready.
- 23/23 individual PDFs are one page; the aggregate is 24 pages.
- Zero overfull boxes.
- 552 stored terms, 138 published terms, and 430 recurrence instances pass.
- Visual QA passed for A120589 and A120588.

## Blockers

None. One transient A244594 PDF short write was detected during QA and resolved
by the atomic publication change; it caused no mathematical state change.

## Proposed next shot

Freeze this certificate layout. Any next pass should be driven by a specific
remaining mathematical or copy-edit discrepancy, not a broad reformat.
