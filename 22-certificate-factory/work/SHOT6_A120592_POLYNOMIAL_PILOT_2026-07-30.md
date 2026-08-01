# Shot 6 report: A120592 generalized polynomial pilot

## Outcome

A120592 passed the generalized q3 term-shift algorithm without a mathematical
normalization change. The existing algorithm only needed its polynomial
`D(u)` and term list supplied as case data.

Input:

    5*A(x)=4+4*x+A(x)^3,
    A(x)=1+2*T(x),
    D(u)=1-3*u-2*u^2,
    rho(u)=u-3*u^2-2*u^3,
    H_n(u)=2/(n*rho(u)^n).

The scalar factor 2 does not change the recurrence or telescoping certificate.

## Exact outputs

Recurrence, valid for n>=1:

    (-108*n^2+12) a(n)
    +(-216*n^2-324*n-108) a(n+1)
    +(17*n^2+51*n+34) a(n+2) = 0.

Certificate:

    R(n,u)=N(n,u)/rho(u),

where

    N(n,u)=
    -72*n*u^4-144*n*u^3+42*n*u^2+114*n*u-17*n
    -24*u^4-48*u^3-6*u^2+6*u.

The recurrence-derived homogeneous ODE is

    12*x^2*A
    +(-108*x^3-108*x^2)*A'
    +(-108*x^4-216*x^3+17*x^2)*A'' = 0.

After removing the common x^2 factor:

    12*A-108*x*(x+1)*A'
    +(17-216*x-108*x^2)*A'' = 0.

## Matrix statistics

- G: 6 by 6.
- nonzero G entries: 18.
- det(G): -68.
- X: 2 by 3.
- rank(X): 2.
- nullity(X): 1.
- pole-lowering steps: 3.
- certificate denominator power: 1.
- degree of N in n: 1.
- degree of N in u: 4.
- measured peak RSS: approximately 60 MiB.
- measured pilot wall time: below 1 second.

## Checks

- D override exact.
- rho=uD.
- G inverse exact.
- G[U;V]=E.
- every encoded input, V contribution, and output of all three lowering steps
  independently replayed.
- replayed columns rebuild X_full.
- final remainder row zero.
- rank 2 and nullity 1.
- X*P=0.
- recurrence residual zero for all stored published terms in the valid range.
- all shifted recurrence scales polynomial.
- cleared telescoping identity zero.
- recurrence-to-ODE series residual zero through the safe emitted range.
- ODE/recurrence coefficient correspondence exact.

All 23/23 pilot checks passed.

## Changed files

- Generalized `build_case` with optional D, term, and normalized-string inputs.
- Added `src/generalized_polynomial_pilot.py`.
- Added `runs/A120592-polynomial-pilot/`.
- Promoted A120592 matrices, recurrence, certificate, and ODE records to
  verified.
- Promoted A120592 to `ANALYTIC_COMPLETE`.
- Added this report.

## Blockers

No A120592 mathematical blocker was found.

The remaining engineering task is to move the optional parameters from the
pilot wrapper into the manifest-driven bounded runner. The observable-power
seed option is still not implemented. Rational descendants remain a separate
direct-x route.

## Proposed next shot

Write the 18 unfinished cases as a checklist ordered by estimated cost and
kernel class. Then process one case per bounded invocation, beginning with the
remaining low-degree polynomial kernels. Do not launch the whole checklist
until the runner records case identity, rho, seed, limits, project size, and
forensic output automatically.
