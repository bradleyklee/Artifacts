---
shot: 22
date: 2026-07-31
scope: final OEIS plaintext and certificate consistency
status: complete
time_limit: 15 minutes
---

# Final OEIS and certificate consistency pass

## Corrections

- Regenerated the canonical OEIS comparison Markdown and paste-ready plaintext
  from the verified 23-case records.
- Replaced the stale root OEIS files with links to the canonical `work/`
  outputs, eliminating two divergent versions.
- Updated every `%H` proposal to `Bradley Klee and Mech.An.ika Sol (Open AI)`
  and retained the per-A-number certificate link.
- Updated all 23 concise certificates, the combined cover, and the verbose
  A120590 certificate to display `Bradley Klee, Mech.An.ika Sol (Open AI)`.
- Rebuilt the verbose certificate portably with Latin Modern fonts; it remains
  16 pages. Its duplicate PDF name is now a link to the current physical PDF.

## OEIS plaintext checks

- Strict target headings: 23/23 in the paste-ready text and 23/23 in the
  comparison Markdown.
- Paste-ready additions: 146 `%F`, `%C`, `%e`, and `%H` lines in total.
- Current affiliation/link line: 23/23 cases.
- Former affiliation in canonical OEIS outputs: 0 occurrences.
- Root and `work/` OEIS paths resolve to byte-identical content.

## Certificate and mathematical checks

- Concise PDFs: 23/23 valid, one page, and carrying the current affiliation.
- Aggregate: valid, 24 pages, with the current affiliation on its cover.
- Verbose A120590 certificate: valid, 16 pages, with the current affiliation.
- Visual checks: aggregate cover, A120589, and verbose A120590 page 1 pass.
- Mathematical audit: PASS for 552 stored terms, 138 published terms, and 430
  recurrence instances.
- Broken symlinks: 0.

## Case states and blockers

- Case states: 23/23 certificate-ready; unchanged mathematically.
- Blockers: none.

## Proposed next shot

None for this package. Treat the returned ZIP as the final internally
consistent release baseline. Future changes should start a new version.
