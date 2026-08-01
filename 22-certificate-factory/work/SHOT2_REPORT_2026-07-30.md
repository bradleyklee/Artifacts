# Shot 2 report: bounded knowledge transfer

## Completed

- Added a bounded one-case runner with 300-second wall, 1024-MiB address-space,
  15-minute shot, and 10-MiB active-project defaults.
- Added forensic JSON checkpoints for size refusal, timeout, memory/process
  failure, nonzero exit, and successful completion.
- Replaced status-only analytic wrappers with full canonical JSON for seven
  components in A120588, A120590, A120593, and A120596.
- Added explicit canonical authority maps to all four manifests.
- Recorded compact, verified q6-q9 knowledge without guessing OEIS mappings.
- Removed redundant nested ZIPs and duplicate q2-q5 run copies from the active
  crawl path. Their hashes and original paths are recorded.

## Files changed

- `WORK_MANIFEST.md`
- `src/bounded_case_runner.py`
- `src/normalize_existing_cases.py`
- Four `manifest.json` and generated `CHECKLIST.md` files
- 28 canonical analytic component JSON files across four cases
- `work/family_status.json`
- `work/blockers.json`
- `work/external_archive_inventory.json`
- `work/unmapped_verified_runs.json`
- `reports/forensics/q999-20260730T190935Z.json` (deliberate size-refusal test)

## Checks run

- Canonical transfer equivalence: 20/20 sampled object comparisons passed.
- Fresh A120590 exact validation: 65/65 passed.
- Manifest/checklist coverage: seven verified analytic components in each of
  four cases.
- Bounded-runner size refusal: passed; no mathematics was started.
- Active project size: 10,329,182 / 10,485,760 bytes.

## Case states

- A120588: `ANALYTIC_COMPLETE`
- A120590: `ANALYTIC_COMPLETE`
- A120593: `ANALYTIC_COMPLETE`
- A120596: `ANALYTIC_COMPLETE`

Canonical analytic component coverage is 4/23 for terms, inverse map,
coefficient formula, matrices, recurrence, certificate, and ODE. Tree coverage
is 0/23.

## Blockers

No mathematical blocker was encountered. The main engineering constraint is
the 10-MiB ceiling: only 156,578 bytes remain. Any new full case must replace or
summarize bulky legacy run data rather than coexist with another duplicate.

The q6-q9 runs are exactly validated but their A-number mappings remain
unresolved. They were not promoted to canonical cases.

## Unresolved structural decisions

None needed now. The attachment's larger archive/schema refactor was not
adopted because it would add navigation and size overhead without increasing
mathematical coverage.

## Proposed next shot

Resolve exactly one q6-q9 A-number mapping from already supplied target
knowledge or a user-provided mapping, then canonicalize that run in place while
removing its bulky legacy duplicate. Do not search the web or compute the whole
family. If no mapping is supplied, work instead on compact schema validation
and certificate-field completeness for the existing four cases.
