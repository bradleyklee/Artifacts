# Shot 9 report: completion pass

## Outcome

All 23 verified targets are now analytically complete.

Coverage:

- typogeometric models: 23/23;
- explicit set enumeration through three leaves: 23/23;
- contour integrands: 23/23;
- exact matrix data: 23/23;
- recurrences: 23/23;
- rational certificates: 23/23;
- linear ODEs: 23/23.

## Observable-power completion

A120589 uses the full two-dimensional remainder space and three shifted
columns. Its primitive relation is

    0*a(n)+(-4*n-2)*a(n+1)+(n+2)*a(n+2)=0.

A120591 uses the full three-dimensional remainder space and four shifted
columns:

    0*a(n)
    +(-27*n^2-54*n-24)*a(n+1)
    +(-162*n^2-567*n-486)*a(n+2)
    +(13*n^2+65*n+78)*a(n+3)=0.

Both exact certificates are rational in n because the observable seed appears
in the certificate denominator. Their cleared rational identities and stored
term checks pass.

A120589 is recorded as the maximality standout: its maximal-degree seed fills
the final remainder direction, forcing dimension+1 columns before nullity.

## Remaining descendants

A244627 passed the numerator-aware direct-x matrix reduction:

- Gx 6 by 6;
- X 2 by 3, rank 2, nullity 1;
- order-two ODE for A', order-four coefficient recurrence;
- exact integrand certificate residual zero.

A244856 passed the same route:

- Gx 8 by 8;
- X 3 by 4, rank 3, nullity 1;
- order-three ODE for A', order-five coefficient recurrence;
- exact integrand certificate residual zero.

## Attached A244856 package

The supplied `A244856_typogeometry_certificate_v1` package was independently
run and all verifier groups passed:

- schema;
- literal grammar counts through n=4 and exact n=2 member set;
- algebraic equation;
- Lagrange/residue terms;
- recurrence;
- exact creative-telescoping identity.

It supplies a shorter order-four term-shift recurrence and certificate.
That order-four result is canonical for A244856; the matrix-derived order-five
recurrence remains as an independent cross-check. No minimality claim is made.
The complete attached package is preserved under A244856 provenance.

## Resource results

- Largest polynomial case: denominator degree 10, G 20 by 20.
- Largest measured polynomial runtime: about 81 seconds.
- Largest measured peak RSS: about 177 MiB.
- No case approached the 1 GiB memory limit.
- Exact payloads are compressed after verification.
- Active project remains below 10 MiB.

## Resolved blockers

- scaled polynomial kernels;
- observable fixed-seed remainder dimension;
- leading-zero recurrence vectors;
- rational-in-n observable certificates;
- rational-descendant numerator-aware x derivatives;
- A244856 independent certificate merge.

## Proposed next shot

Do not generate more mathematics. Audit the 23-case checklist and canonical
pointers, regenerate family summaries/checklists, remove stale blocker labels,
and produce a compact completion index suitable for human review.
