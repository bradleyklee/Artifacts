# Exact icosahedral branch-point Tschirnhaus map — v1

## Result

Let the icosahedral quotient branch polynomial be

    f_R(R,beta)
      = -R^3 +(4-65*beta)R^2
        +beta*(720*beta^2+200-795*beta)R
        +500*beta^2-2275*beta^3+3440*beta^4-1728*beta^5.

Let the native signature-4 branch-label polynomial be

    F_z(z,beta)
      = N(beta)*(4-3*z)^3
        -4*P(beta)^3*z^2*(1-z),

where

    P(beta) = 135*beta^3 + 115*beta^2 + 5*beta + 1,

    N(beta) = beta^2*(1-beta)^5*(27*beta+5)^3.

Define

    Q(beta) = 729*beta^5 + 5130*beta^4 + 1870*beta^3 + 480*beta^2 - 15*beta - 2,

    U(beta) = 531441*beta^9 - 2086398*beta^8 + 5089149*beta^7 - 2554767*beta^6 + 891211*beta^5 + 347561*beta^4 - 97793*beta^3 - 23261*beta^2 + 8*beta + 1,

    V(beta) = 2834352*beta^9 - 17025795*beta^8 + 20685375*beta^7 - 11753325*beta^6 + 1314795*beta^5 + 2556001*beta^4 - 477155*beta^3 - 211455*beta^2 - 19895*beta - 50.

Then the exact quadratic Tschirnhaus map is

    R = A(beta)*z^2 + B(beta)*z + C(beta),

with

    A(beta) = -9*Q(beta)/(4*P(beta)),

    B(beta) = (7*beta+1)*U(beta)/(P(beta)*Q(beta)),

    C(beta) = -beta*V(beta)/(P(beta)*Q(beta)).

Exact symbolic polynomial division gives

    f_R(A*z^2+B*z+C,beta) = 0 mod F_z(z,beta).

Equivalently, every root of the z-cubic maps to a branch point of the
icosahedral quotient cubic.

## How it was found

1. Exact number-field isomorphisms were computed on rational fibers.
2. The three coefficient values were sampled on 24 fibers.
3. Rational interpolation found degrees:
   - A: numerator degree 5, denominator degree 3;
   - B: numerator degree 10, denominator degree 8;
   - C: numerator degree 10, denominator degree 8.
4. Held-out fibers agreed exactly.
5. The resulting formulas passed a symbolic remainder test over Q(beta).

## Important correction

A Möbius map exists on each numerical fiber after choosing three root
pairings, but its coefficients are generally not rational functions of beta.
That was an over-strong ansatz.

The correct rational relation between two generators of a cubic extension is
quadratic:

    R = A*z^2+B*z+C.

## Interpretation

This does not make z a coordinate varying along the elliptic fiber.  It maps
the three possible z-branches to the three finite branch points S=0 of the
icosahedral cubic.  Its purpose is to label and pair those branch points
algebraically.

This is precisely the missing data needed to construct the edge-adapted
cross-ratio and hence the even quartic coordinate.

## Next step

Choose the physical edge branch z=z_edge(beta).  Its associated branch point is

    r_edge(beta)=A*z_edge^2+B*z_edge+C.

Use the other two conjugate z-roots to obtain the remaining branch points.
Then construct a cross-ratio coordinate whose four ramification points are
paired as

    {r_edge, infinity} and {r_2,r_3}

or the alternative D2 pairing selected by the real cycle.

The cross-ratio is then normalized to the known even quartic

    12*y^2=-x^4+(2+12*alpha)x^2+4*alpha-1.

The certificate supplies the final map from (x,y) to (p,q).
