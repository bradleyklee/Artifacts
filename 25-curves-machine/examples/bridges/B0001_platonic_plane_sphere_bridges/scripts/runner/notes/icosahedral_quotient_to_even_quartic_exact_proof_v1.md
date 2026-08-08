# Exact proof: icosahedral quotient cubic to even quartic

## Statement

Let

    S^2 = -(R-e1)(R-e2)(R-e3)

and define the edge-first cross-ratio parameter

    k^2 = (e3-e1)/(e3-e2).

Choose `a,b` so that

    k = (a-b)/(a+b),

equivalently

    a = b(1+k)/(1-k).

Set

    D(R) = (1-k)R-(e1-k e2),

    x = b*((1+k)R-(e1+k e2))/D(R),

    y = b*(a-b)(e2-e1)
        /(sqrt(3)*sqrt(e3-e2))
        *S/D(R)^2.

Then identically,

    12 y^2 + x^4 -(a^2+b^2)x^2 + a^2 b^2 = 0.

Equivalently,

    12 y^2 = -(x^2-a^2)(x^2-b^2).

For the triangle–rectangle family,

    a^2+b^2 = 2+12 alpha,

    a^2 b^2 = 1-4 alpha,

so this becomes exactly

    12 y^2 =
      -x^4 +(2+12 alpha)x^2 +4 alpha-1.

## Proof method

The verification uses only the two defining relations

    S^2 = -(R-e1)(R-e2)(R-e3),

    k^2 = (e3-e1)/(e3-e2).

The second relation is solved as

    e3 = (k^2 e2-e1)/(k^2-1).

After substituting both relations into

    12 y^2 + x^4 -(a^2+b^2)x^2 + a^2 b^2,

SymPy simplifies the rational expression to exactly zero.

This is a generic algebraic identity. It is not merely a numerical test and
does not depend on special values of beta.

## Consequence for the icosahedral problem

The previous exact Tschirnhaus map sends the three roots of the signature-4
cubic to the three finite branch points `e1,e2,e3` of the icosahedral quotient
cubic.

Therefore, after choosing the physical edge-first ordering and square-root
branches, the icosahedral quotient cubic maps exactly to the
triangle–rectangle even quartic.

Composing with the already-known certificate map gives an exact algebraic map

    (R,S) -> (x,y) -> (p,q)

over the branch field.

## What is now solved

Solved exactly:

1. the icosahedral base change `beta -> z -> alpha`;
2. the branch-point Tschirnhaus correspondence;
3. the edge-first D2 cross-ratio;
4. the quotient cubic to even-quartic map;
5. the even quartic to triangle–rectangle Hamiltonian map.

## What remains genuinely open

Not yet solved:

1. substitute and simplify the explicit original sphere invariants `R(J),S(J)`;
2. track the exact physical Lie–Poisson differential;
3. prove the global real-cycle continuation;
4. determine whether face-first and vertex-first sectors use the same plane
   model through other branches.

Thus the quotient-level birational correspondence is closed. The remaining
work is the physical lift to the original sphere dynamics, not the elliptic
curve map itself.
