---
shot: 21
date: 2026-07-31
scope: packaging and reproducible-junk cleanup
status: complete
time_limit: 15 minutes
---

# Minimal-footprint and aggregate-propagation pass

## Propagation result

The complete project contains one physical aggregate at
`release/ALL_23_CERTIFICATES_RHO_INLINE_v9.pdf`. It is a valid 24-page PDF of
928,171 bytes. `release/HANNA_23_CALCULUS_CERTIFICATES.pdf`, the legacy release
names, and the root-level legacy aggregate are compatibility symlinks to that
same physical file. The packaged ZIP preserves those links and therefore does
not store duplicate aggregate bytes.

## Removed as reproducible junk

- Per-case TeX auxiliary, output, temporary-build, and duplicate build-log
  files.
- Aggregate TeX auxiliary, output, and build-log files.
- Two duplicate physical copies of the aggregate PDF, replaced by symlinks.

Canonical validation logs under `checks/` were retained. Canonical case data,
source, reports, the verbose A120590 certificate, individual current PDFs and
TeX sources, embedded payloads, and compatibility paths were retained.

## Footprint and checks

- Project logical byte count after cleanup: 15,297,895 bytes.
- Broken symlinks: 0.
- Individual PDFs: 23/23 valid and one page.
- Aggregate PDF and its main compatibility link: valid and 24 pages.
- Aggregate embedded payload index: present.
- Most recent mathematical audit remains PASS: 552 stored terms, 138
  published terms, and 430 recurrence instances.

The retained footprint cannot reasonably be pushed below 10 MiB without
removing substantive canonical material: the 23 human PDFs alone occupy about
5.9 MB, and the remaining large objects include canonical case records, the
reviewed verbose A120590 example, reports, and exact payloads.

## Case states and blockers

- Case states: 23/23 certificate-ready; unchanged mathematically.
- Blockers: none.

## Proposed next shot

Treat this as the clean release baseline. Further size reduction should use a
separate source-only or certificates-only distribution profile rather than
deleting canonical data from the complete project.
