---
shot: 14
date: 2026-07-31
scope: 23 canonical cases
status: complete
---

# Enriched one-page certificate pass

## Changed

- Rebuilt all 23 case certificates as exactly one page each and reassembled the 24-page portfolio.
- Added constrained binomial/multinomial coefficient sums for primary and rational-descendant cases; companion cases show the exact ordered convolution sum.
- Printed exact `G`, `U`, `V`, and `J` matrices when their dimensions and entry lengths remain legible. Larger matrices retain exact canonical-source pointers, dimensions, and embedded hashes.
- Added an explicit telescoping identity and the verified rational certificate `R` or `C` on every page. Oversized numerators remain exact in the embedded payload/canonical record.
- Added `Delta_k : multiplicity` annotations next to every typogeometric model, including marked constructors and inherited companion multiplicities.
- Broke longer differential equations across aligned display lines.

## Checks

- 23/23 individual PDFs: exactly one page.
- 23/23 TeX logs: zero overfull boxes.
- Combined portfolio: 24 pages (cover plus 23 certificates).
- Exact arithmetic audit: 552 stored terms, 138 published-prefix terms, and 430 recurrence instances pass.
- Embedded payload extraction and byte comparison: 23/23 pass.
- Rendered visual inspection: low-order primary, q=3 primary, companion, high-order colored case, and rational descendant pass.

## Case states

All 23 cases remain `verified` / certificate-ready. No mathematical status was advanced or weakened by the presentation pass.

## Blockers

None. Large matrices and high-degree telescoper numerators are intentionally kept in exact embedded/canonical payloads because printing them at one-page scale would be unreadable.

## Proposed next shot

Editorial review of notation consistency against the q=3 human certificate, followed by case-by-case OEIS submission shortening without changing mathematical content.
