# Shot 3 report: all-target attempt

## Completed

- Verified the defining equations and leading terms of all 20 core targets and
  all three direct-composition descendants against OEIS.
- Identified the non-pattern cases explicitly; no A-number was inferred merely
  from adjacency.
- Generated 24 exact terms for every target from its defining equation.
- Emitted exact case specifications, inverse-map descriptions, and coefficient
  formulas for every target.
- Promoted the already validated q6 run to A120600 after its OEIS terms and
  equation matched exactly.
- Attempted every target against the current RELAY capability and recorded the
  first unsupported kernel class instead of silently skipping it.

## Files changed

- `src/expand_target_coverage.py`
- Canonical case directories for all 23 targets
- `work/family_status.json`
- `work/blockers.json`
- `work/external_archive_inventory.json`
- This report

## Checks run

- OEIS leading-prefix checks: 138/138 terms matched.
- Defining-equation integrality/generation: 552/552 terms produced exactly.
- Required case directories: 23/23 present.
- Fresh A120600 full RELAY validation: 146/146 exact checks passed.
- Active project remains below 10 MiB.

## Case states

- `ANALYTIC_COMPLETE`: 5/23
  - A120588, A120590, A120593, A120596, A120600
- `PARTIAL`: 18/23

Component coverage:

- terms: 23/23
- inverse map: 23/23 verified or not applicable
- coefficient formula: 23/23
- matrices: 5/23
- recurrence: 5/23
- telescoping certificate: 5/23
- ODE: 5/23
- tree model: 0/23

## Blockers

Three shared engineering/mathematical blockers remain:

1. Thirteen non-normalized core cases require RELAY to accept the emitted
   scaled polynomial kernel instead of the hard-coded normalized `D_q`.
2. A120589 and A120591 require a proved certificate/ODE transfer through
   `A(x)^2` and `A(x)^3`.
3. A244594, A244627, and A244856 require rational or
   denominator-cleared inverse-map reduction.

These are recorded per case and component in `work/blockers.json`.

## Ambiguities requiring human decision

Full exact matrices and certificate payloads for another 18 cases are unlikely
to coexist uncompressed under the 10-MiB active-folder ceiling. Choose one:

- permit compressed per-case exact payloads in the active project;
- keep the 10-MiB controller repository and store exact case payloads as
  separately retained artifacts;
- raise the active-folder ceiling.

## Proposed next shot

Generalize the polynomial-kernel entry point and pilot it on A120592, A120594,
and A120595. If all exact identities pass, run the remaining ten scaled
polynomial core cases one at a time, retaining payloads according to the chosen
size policy. Handle observable powers and rational descendants afterward.
