# Shot 4 report: typogeometric and contour coverage

## Scope and bounds

- Order followed: geometric definition, contour definition, algebraic
  differential fallback, then matrix work.
- Scope: A120588--A120607 first, followed by A244594, A244627, A244856.
- Hard limits: 15-minute shot, 300 seconds per process, 1024 MiB address space,
  10,485,760 project bytes.
- Matrix extraction was not started in this shot.

## Statistical coverage

- Typogeometric models: 23/23 verified.
- Contour definitions: 23/23 verified.
- Algebraic first-order differential relations: 21/23 verified directly.
- Observable-power differential systems: 2/23 produced; scalar elimination is
  pending.
- Grammar-to-series comparisons: 529/529 exact coefficients passed (23
  positive-index coefficients for each of 23 cases).
- Existing defining-equation terms: 552/552 retained.
- Existing OEIS prefix comparisons: 138/138 retained.
- JSON parse check: 389/389 JSON files passed.
- Active project size after generation: 5,077,703 bytes.

## Mathematical result

For each primary case, the canonical shift gives

    A(x) = 1 + d*T(x),
    T = x + sum_{k=2}^q c_k*T^k.

All emitted `c_k` are nonnegative integers. Thus every primary case has a
finite-color unweighted plane-tree grammar. The normalized cases have the
literal full-slot grammar `c_k=binomial(q,k)`. A depth-first word uses
`Delta_k` of weight `k-1` and true leaf `l` of weight `-1`; false leaves restore
the unused positions of the full ordered slot model.

The two observable powers are ordered forests of their parent
typogeometries. Each descendant also has a positive grammar:

- A244594: `T=x+x*T+3*T^2+T^3`.
- A244627: `T=x+2*x*T+3*T^2+2*T^3`.
- A244856: `T=x+x*T+6*T^2+4*T^3+T^4`.

Here `x*T` is encoded by a genuinely binary marked `Delta_2` node containing
one new true leaf and one recursive subtree, so it does not introduce unary
pass-through.

Every case now has a Lagrange/Cauchy contour record. The primary and descendant
records use `rho(u)=u*D(u)` or the rational analogue `rho(u)=u*E(u)`. The
observable powers use the parent kernel with the Lagrange derivative factor.

## Changed files

- Added `src/expand_typogeometric_coverage.py`.
- Added `data/contour.json` in all 23 case directories.
- Replaced `data/tree_model.json` in all 23 case directories.
- Replaced `data/ode.json` in all 23 case directories.
- Updated all 23 manifests and generated checklists.
- Added `reports/typogeometric_coverage.json`.
- Updated `work/family_status.json` and `work/blockers.json`.
- Added this report.

## Case states

Top-level states remain unchanged because matrices, recurrences, and
telescoping certificates were deliberately not generated:

- `ANALYTIC_COMPLETE`: 5/23.
- `PARTIAL`: 18/23.

## Blockers

1. Thirteen scaled core kernels still need the exact G/U/V shift-reduction
   entry point generalized beyond the normalized hard-coded kernel.
2. A120589 and A120591 need elimination of the parent series to obtain scalar
   linear ODEs and transferred recurrence/certificate data.
3. The rational descendant kernels need exact denominator-aware G/U/V and
   direct-derivative reductions.
4. Full matrix payloads for 18 additional cases may approach the active-folder
   ceiling; generate one case at a time and retain compact sparse/statistical
   data before deciding which full payloads stay active.

## Proposed next shot

Pilot exact derivative and shift matrices on A120592, the easiest uncompleted
primary case. First construct and verify the direct derivative reduction from
its algebraic relation; then generalize the polynomial-kernel G/U/V path and
compare the two scalar linear ODEs. Stop after A120592 or at the first exact
rank/residual mismatch. If it passes within the size bound, apply the same
bounded process to A120594 and A120595 in the following shot.
