---
shot: 15
date: 2026-07-31
scope: 23 canonical one-page certificates and aggregate portfolio
status: complete
---

# Readability and picture-multiplicity pass

## Changed

- Increased the document base size from 10 pt to 11 pt.
- Increased line spacing, paragraph spacing, section spacing, tree scale, and tree-label size.
- Added a bold `x m` annotation directly beneath every pictured brace code whenever the displayed color-erased shape represents `m > 1` enumerated words.
- Retained multiplicity one without visual clutter.
- Kept the separate constructor multiplicity line because constructor counts and whole-picture multiplicities answer different questions.
- Rebuilt every individual certificate and the aggregate portfolio.

## Multiplicity rule

For colored and forest models, the annotation is the exact count of enumerated raw words that become the pictured brace word after constructor-color labels are erased. Literal positional models retain their explicit `0/1` slots and therefore have multiplicity one per pictured code.

Examples:

- A120607: `1 x 3`, `{1,1} x 15`, `{1,{1,1}} x 75`, `{1,1,1} x 120`.
- A244594: `{1,1} x 4`, `{1,{1,1}} x 16`.

## Checks

- 23/23 individual PDFs are exactly one page.
- 23/23 TeX logs contain zero overfull boxes.
- Aggregate PDF is 24 pages and contains all revised case pages.
- Exact arithmetic audit still passes 552 stored terms, 138 published-prefix terms, and 430 recurrence instances.
- Embedded payload checks remain 23/23 passing.
- Latest rendered q=3, high-order colored, and rational-descendant pages were visually inspected.

## Case states and blockers

All 23 cases remain verified. No mathematical blockers were introduced. The only reduction was presentational: a redundant long normalization polynomial is summarized when its coefficients are already printed as the constructor multiplicity line.

## Proposed next shot

If desired, tune the four chosen sample trees per case so that the displayed gallery favors the most structurally distinctive high-multiplicity shapes rather than always using the current leaf/binary/nested/ternary template.
