# Curve-model search plan

## Current boundary

Two quartic strata are implemented:

1. two fixed nodes at infinity;
2. one fixed tacnode at infinity.

The tacnode stratum adds plane presentations but generically repeats
`III*+I1+I1+I1`. Do not call the quartic search complete yet.

## Next quartic work

1. Solve delta-two unibranch singularities at infinity, especially the
   ramphoid-cusp boundary.
2. Split degenerate tacnode cases by exact local branch type and compute their
   invariant degree profiles.
3. Check whether the existing two-node parameterization covers all small
   rational presentations, not merely the geometric class over an algebraic
   closure.
4. For every retained normal form, derive `c4`, `c6`, and `Delta` before any
   coefficient scan.

## Beyond quartics

For a degree-`d` pencil, prescribe a singularity cluster at infinity whose
combined delta lowers the arithmetic genus to one. Search the local equations
first; only then enumerate small rational coefficients. Quintics with total
delta five are the first next-degree target.

## Record format

Every branch must write:

```text
normal form
local singularity conditions
generic genus check
c4, c6, Delta degree profile
realized fiber configurations
explicit witnesses
period status
Laurent status
OEIS status
failure or stop reason
```
