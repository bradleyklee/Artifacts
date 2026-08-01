# Shot 1 report: infrastructure migration

Scope: infrastructure migration only. No family-wide generation or tree-model
search was started.

## Statistical coverage

- Existing q-labelled examples mapped: 4/4.
- Strict target queue represented by migrated analytic cases: 4/23 (17.4%).
- Standard required non-PDF paths present for migrated cases: 80/80.
- Existing stored validation checks represented: 314/314 pass
  (q2 50/50, q3 65/65, q4 86/86, q5 113/113).
- Fresh exact validation after migration: A120590 65/65 pass.
- Tree-model attempts: 0/4, by Shot 1 scope.
- Canonical complete release payloads copied: 1/23 (A120590).

## Verified mappings and case states

| Legacy alias | Canonical case | Mapping evidence | State |
| --- | --- | --- | --- |
| q2 | A120588 | defining equation and leading terms | ANALYTIC_COMPLETE |
| q3 | A120590 | defining equation and leading terms | ANALYTIC_COMPLETE |
| q4 | A120593 | defining equation and leading terms | ANALYTIC_COMPLETE |
| q5 | A120596 | defining equation and leading terms | ANALYTIC_COMPLETE |

The OEIS leading terms used for the four matches are stored in each manifest.
The q3 mathematical files and release candidate were moved without alteration;
its existing payload and PDF were additionally copied to canonical release
paths.

## Files and infrastructure added

- `schemas/case-manifest.schema.json`
- `src/migrate_manifest_cases.py`
- Four canonical case manifests and standard directory skeletons
- Generated `CHECKLIST.md` and provenance hashes for each migrated case
- This report

The original example directories were renamed, not regenerated:
`q2 -> A120588`, `q3 -> A120590`, `q4 -> A120593`, and
`q5 -> A120596`. The q-label remains in manifest metadata.

## Checks and blockers

The default environment initially lacked SymPy. A temporary SymPy 1.13.3
installation was used for the fresh q3 validation; this did not alter the
repository. The repository already declares SymPy in `requirements.txt`.

No mathematical blocker or mapping ambiguity was found. Incomplete coverage is
intentional:

- 19/23 strict targets have no canonical case directory yet.
- Only A120590 has a canonical complete release payload and certificate.
- Canonical JSON files for the other migrated cases currently record status and
  point to preserved legacy data; they are not yet normalized full payloads.
- Tree models remain `not_attempted`.

## Proposed next shot

Shot 2 should run only the four-case analytic pilot
(A120588, A120590, A120593, A120596), normalize the preserved analytic objects
into full canonical JSON payloads, and report matrix dimensions, recurrence/ODE
minimality questions, and exact failures. It should not attempt tree models or
the remaining 19 targets.
