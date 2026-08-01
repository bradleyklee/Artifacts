---
shot: 16
date: 2026-07-31
scope: 23 one-page certificates and aggregate portfolio
status: complete
---

# Visible multiplier badges

The earlier labels omitted `x1` and rendered nontrivial multipliers too much like ordinary caption text. This pass replaces them with a bordered red badge beside every pictured brace code.

Examples now visibly read:

- A120590: `1 x1`, `{1,1,0} x1`, `{0,1,1} x1`, `{1,1,1} x1`.
- A120607: `1 x3`, `{1,1} x15`, `{1,{1,1}} x75`, `{1,1,1} x120`.

Checks:

- Four `xN` badges detected on every one of the 23 aggregate case pages.
- 23/23 individual PDFs remain exactly one page.
- Zero overfull boxes.
- Aggregate remains 24 pages.
- Exact arithmetic and embedded-payload audit remains passing.
- Literal and high-multiplicity aggregate pages were rendered and visually inspected.

All 23 case states remain verified. There are no blockers. The next optional design question is whether the badge color should remain red or be changed to the document's navy/orange palette.
