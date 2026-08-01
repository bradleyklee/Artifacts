# Shot 7 report: A244594 rational-descendant pilot

## Outcome

The odd-case direct-x reduction works, but it requires one genuine extension
to the normalized q3 pseudocode.

For A244594:

    (4-x)A(x)=3+A(x)^3,
    T=A-1,
    T=x+x*T+3*T^2+T^3,
    rho(u)=(u-3*u^2-u^3)/(1+u).

Thus

    A'(x)=Res Phi(x,u) du,
    Phi(x,u)=(1+u)/(u-3*u^2-u^3-x*(1+u)).

Write `h=1+u` and `g=u-3*u^2-u^3-x*(1+u)`. Then

    D_x^j Phi = j!*h^(j+1)/g^(j+1).

The numerator therefore changes with every x derivative. The correct
algorithm first polynomial-divides each `h^(j+1)` by `g`, then lowers every
resulting pole component with the same Gx/Ux/Vx matrices.

## Exact ODE

The corrected derivative-remainder nullvector gives

    (4*x^2-32*x+64) A'
    +(14*x^3-168*x^2+672*x-1139) A''
    +(4*x^4-64*x^3+384*x^2-781*x+52) A''' = 0.

This is an order-two equation for A' and an order-three equation for A.

## Exact recurrence

Valid on the checked positive-index range:

    (4*n^3+2*n^2-2*n) a(n)
    +(-64*n^3-168*n^2-136*n-32) a(n+1)
    +(384*n^3+1824*n^2+2848*n+1472) a(n+2)
    +(-781*n^3-5825*n^2-14286*n-11520) a(n+3)
    +(52*n^3+468*n^2+1352*n+1248) a(n+4) = 0.

## Matrix and certificate statistics

- Gx: 6 by 6, with 21 nonzero entries.
- det(Gx): `4*x^3-48*x^2+192*x-13`.
- Corrected X: 2 by 3.
- rank(X): 2; nullity: 1.
- Certificate denominator: `g(x,u)^2`.
- Certificate numerator degree in x: 3.
- Certificate numerator degree in u: 5.
- Runtime: about 1.6 seconds.
- Peak RSS: about 64 MiB.

## Checks

Nine independent grouped checks passed:

- Gx invertible.
- Gx/Ux/Vx exact split.
- Gx inverse replay.
- corrected numerator-aware integrand certificate residual zero.
- corrected X rank 2 and nullity 1.
- recurrence matches every stored published term in range.
- recurrence-derived ODE series residual zero.
- recurrence/ODE coefficient correspondence exact.
- the old normalized-q3 translator is explicitly detected as inapplicable.

## Important failed attempt retained

The first fixed-seed adaptation was wrong because it treated
`D_x^j(h/g)` as `j!*h/g^(j+1)`. Its internal formal certificate was exact,
but its ODE failed the sequence coefficients immediately. The forensic record
is retained under `reports/forensics/`.

This distinction matters for the other two descendants: reuse Gx/Ux/Vx, but
generate numerator-aware derivative columns.

## Changed files

- Generalized `src/direct_ode_reduction.py` to expose denominator and seed
  inputs.
- Added `src/odd_descendant_pilot.py`.
- Added `runs/A244594-direct-x-pilot/`.
- Added a forensic record for the rejected fixed-seed attempt.
- Promoted A244594 matrices, recurrence, certificate, and ODE to verified.
- Promoted A244594 to `ANALYTIC_COMPLETE`.
- Updated family coverage to 7/23.
- Added this report.

## Proposed next shot

The structural obstacle is cleared. Before takeoff, move the corrected
numerator-aware derivative-column construction into the reusable direct-x
module and add the 16 unfinished cases to an ordered, resumable checklist.
Then process one case per bounded subprocess, retaining only canonical payloads
and compact statistics.
