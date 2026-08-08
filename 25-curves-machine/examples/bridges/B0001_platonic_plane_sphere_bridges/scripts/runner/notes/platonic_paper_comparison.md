# Comparison with *The Platonic Elliptic Surfaces*

## Main correction

The octahedral object comes in three distinct layers:

1. the original level curve on the sphere, generically of genus 9;
2. its quotient by the octahedral rotation group, the elliptic surface `234III`;
3. explicit Laurent plane models, which can instead realize the degree-2
   isogenous companion `126III`.

Thus a genus-one plane Hamiltonian should not be expected to be birational to
the full octahedral sphere curve.  The meaningful tests are:

- descent to the rotation quotient;
- equality of the descended period differential;
- or an isogeny to the quotient followed by a possible lift.

## Exact energy-coordinate dictionary

For the paper's octahedral invariant

    q = Jx^2*Jy^2 + Jy^2*Jz^2 + Jz^2*Jx^2,

on the unit sphere,

    alpha_dissertation = 2 - 4*q.

The two OEIS coordinates are

    A318245 / O(4): x4 = 3*q/16,
    A186375 / O(3): x3 = (1-3*q)/4.

Substitution proves that their two rational `1728/j` pullbacks are one and
the same global octahedral map.

## One global K description

Put

    s = sqrt(1-3*q).

Then the square-well and triangular-well Legendre parameters are

    m_O4 = (1-s)^2*(1+2*s)/(4*s^3),

    m_O3 = 4*s^3/((1-s)^2*(1+2*s)),

so

    m_O3*m_O4 = 1.

Each physical well selects the branch that runs from `m=0` at its circular
point to `m=1` at the common saddle.  This is the clean geometric reason to
add the `2F1(1/2,1/2;1;m)` / `EllipticK(m)` form to both OEIS pages, while
retaining the rational `2F1(1/12,5/12;1;1728/j)` form.

## The paper's explicit plane models

The paper gives

    F_O3 = (y+2*x+1)*(x*y+x+2*y)/(x*y),

and

    F_O4 =
      (x*y-x+3*y+1)*(x*y+3*x-y+1)/(x*y).

Their torus constant-term periods reproduce A186375 and A318245.  Table 10
shows that these simple Laurent models live naturally on `126III`, which is
2-isogenous to the sphere quotient `234III`.

This means an equality-of-j test against `234III` alone is too restrictive.
The triangle-rectangle family must be tested against both:

    j_TR = j_234,

and

    Phi_2(j_TR,j_234) = 0,

with the latter containing the direct equality locus `j_TR=j_126`.

## What is already ruled out

The base `j`-map degrees are

    triangle-rectangle: 6,
    234III:             9,
    126III:             9.

Therefore there is no nonconstant rational energy substitution in either
direction that identifies the complete triangle-rectangle family with either
octahedral family.  This does not rule out an algebraic correspondence,
isogeny, quotient, or branched lift.

## Next concrete test

Use the explicit sphere quotient

    S^2 =
      -27*R^3
      + (18*q-4)*R^2
      + q^2*(1-4*q)*R

and compare its invariant differential, and the invariant differential on its
2-isogenous `126III` companion, with the triangle-rectangle differential.
The comparison must include the period scaling, not only the `j`-map.
