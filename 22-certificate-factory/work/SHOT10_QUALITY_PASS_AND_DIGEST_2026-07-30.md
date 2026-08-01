# Shot 10 report: quality pass and complete calculus digest

## Outcome

Generated `work/CALCULUS_DIGEST_23_CASES.md`, with one subsection for every
specified A-number.

The digest includes:

- defining equation and contour kernel;
- reduction route;
- G/Gx, U/Ux, V/Vx, J, and X dimensions;
- canonical recurrence and validity start;
- `P_x` coefficient-matrix dimensions and complete entries, with shift powers
  `x^r` on rows and powers `n^k` on columns;
- verified scalar linear ODE order;
- exact recurrence regeneration of the stored terms;
- comparison with the published OEIS prefix;
- special notes for A120589 and A244856.

## Exact audit totals

- Cases: 23/23.
- Case subsections: 23.
- Stored algebraic terms checked: 552/552.
- Published OEIS prefix terms checked: 138/138.
- Recurrence divisions producing integers: all passed.
- Maximum recurrence residual: zero in every case.
- Analytically complete cases: 23/23.
- Active blockers: zero.

## Quality repair

The five legacy normalized cases had verified scalar linear ODEs inside their
`case.json` payloads, but `data/ode.json` still pointed only to an earlier
nonlinear algebraic differential fallback. The canonical pointers were
repaired for:

- A120588;
- A120590;
- A120593;
- A120596;
- A120600.

No mathematics changed. The repair makes the declared 23/23 linear-ODE
coverage true at the canonical-file level.

## Dimension findings made explicit

For the seed-one polynomial family with denominator degree d:

- G is `2d × 2d`;
- X is `(d-1) × d`;
- the recurrence and scalar linear ODE normally have order `d-1`.

The observable powers use the full remainder space:

- A120589: X is `2 × 3`; `P_x` is `3 × 2`;
- A120591: X is `3 × 4`; `P_x` is `4 × 3`.

The descendants use denominator matrices governed by their direct-x
polynomial degree, while their coefficient recurrences can be longer:

- A244594 and A244627: Gx `6 × 6`, X `2 × 3`, canonical `P_x` `5 × 4`;
- A244856: Gx `8 × 8`, X `3 × 4`, canonical attached `P_x` `5 × 4`.

## Files

- Added `src/generate_calculus_digest.py`.
- Added `src/quality_repair_linear_ode_pointers.py`.
- Added `work/CALCULUS_DIGEST_23_CASES.md`.
- Added `reports/calculus_digest_audit.json`.
- Repaired five canonical ODE pointer files.
- Added this report.

## Claim supported

Within the strict 23-case scope fixed in `work/targets.json`, the complete
calculus chain is present and checked:

    typogeometry
      -> generating equation
      -> contour integrand
      -> exact reduction matrices
      -> nullspace relation
      -> recurrence and rational certificate
      -> scalar linear ODE
      -> exact regenerated terms
      -> published-prefix agreement.

No claim is made that every displayed recurrence or ODE is minimal.
