# Shot 11: full calculus evidence report

## Outcome

Generated `work/FULL_CALCULUS_EVIDENCE_23_CASES.md`, a 23-case report that
prints the complete normalized mathematical payloads and the full derivation
records behind the concise calculus digest.

## Changed files

- `src/generate_full_calculus_evidence.py`
- `work/FULL_CALCULUS_EVIDENCE_23_CASES.md`
- `reports/full_calculus_evidence_audit.json`
- `work/SHOT11_FULL_EVIDENCE_REPORT_2026-07-30.md`

## Checks

- 23/23 required A-number evidence headings.
- 23/23 tree-model payloads printed.
- 23/23 contour payloads printed.
- 23/23 matrix payloads printed.
- 23/23 recurrence payloads printed.
- 23/23 ODE payloads printed.
- 369 source payloads printed with byte counts and SHA-256 hashes.
- 23/23 canonical `checks/results.json` records have status `verified`.
- 46/46 recorded individual checks have status `pass`.
- 552 stored exact terms are present (24 per case).
- Metadata header and standard-symbol notation section are present.

## Case states

All 23 strict targets remain `ANALYTIC_COMPLETE`. This documentation pass
changes no mathematical state.

## Blockers

No mathematical blocker. The current shell lacks the optional SymPy dependency
used by the older concise-digest generator, so that already-generated digest
was not regenerated during this pass. The new evidence report generator has no
SymPy dependency and completed successfully.

## Proposed next shot

Independent human or computer-algebra review of a sample spanning the three
reduction types: A120590 (ordinary term-shift), A120589 (full-remainder extra
shift/maximality case), and A244856 (numerator-aware descendant with attached
order-4 and independent order-5 certificates).
