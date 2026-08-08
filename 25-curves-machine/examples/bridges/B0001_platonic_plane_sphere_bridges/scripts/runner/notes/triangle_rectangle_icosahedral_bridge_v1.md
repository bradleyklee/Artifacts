# Triangle–rectangle and the icosahedral sphere family: stage 1

## Result

There is a direct invariant-theory bridge, but it is structurally different
from the octahedral bridge.

For the octahedron, quotienting by the tetrahedral subgroup `A4 < S4`
immediately produced a genus-one even quartic, which was exactly the
triangle–rectangle model.

For the icosahedron, the corresponding subgroup is

    A4 < A5,

of index five.  The quotient is generically a smooth **genus-three plane
quartic**, not an elliptic curve.  It then maps with degree five to the full
icosahedral elliptic quotient `235II`.

Thus the same coordinates occur, but one extra genus-two part remains.

## 1. The same tetrahedral invariants occur

After an exact orientation-preserving orthogonal change of sphere coordinates,
put

    P = X^2+Y^2+Z^2,

    A = X^2*Y^2 + Y^2*Z^2 + Z^2*X^2,

    r = X*Y*Z,

    s = (X^2-Y^2)*(Y^2-Z^2)*(Z^2-X^2).

These are the same tetrahedral variables used in the octahedral bridge.
In particular, `r` and `s` became the two coordinates of the
triangle–rectangle even quartic.

The icosahedral degree-six Hamiltonian becomes exactly

    Q_I =
      (5/2)*P*A
      -(55/2)*r^2
      +(5*sqrt(5)/2)*s.

On the unit sphere,

    h =
      (5/2)*A
      -(55/2)*r^2
      +(5*sqrt(5)/2)*s.

This is the strongest immediate connection: the triangle–rectangle
coordinates `r,s` occur literally and linearly inside the icosahedral
Hamiltonian.  The new ingredient is the varying quartic invariant `A`.

## 2. The A4 intermediate quotient

The tetrahedral invariant relation is

    s^2 =
      -4*A^3 + A^2 + 18*r^2*A -(4+27*r^2)*r^2.

Eliminating `s` using the icosahedral energy `h` gives

    125*A^3
      -25*A^2
      -5*A*h
      -700*A*r^2
      +h^2
      +55*h*r^2
      +1600*r^4
      +125*r^2 = 0.

This is a plane quartic.  The verifier checks a generic fibre (`h=2`) is
smooth, including its point at infinity, so its generic genus is three.

This explains why the octahedral calculation closed immediately while the
icosahedral one does not:

    octahedral / A4  -> genus 1,

    icosahedral / A4 -> genus 3.

## 3. Exact degree-five map to the elliptic quotient

The paper's degree-ten icosahedral invariant simplifies on the A4 quotient to

    R_I =
      5*(4*A-1)*(-20*A+3*h+320*r^2).

Define

    C =
      -24000*A^3 +14800*A^2 -540*A*h
      -25600*A*r^2 -2500*A
      +33*h^2 +5440*h*r^2 +50*h
      +204800*r^4 +125,

and

    S_I = (8*sqrt(5)/5)*r*C.

Then, modulo the genus-three quartic,

    S_I^2 =
      -R_I^3
      +(4-65*h)*R_I^2
      +h*(720*h^2+200-795*h)*R_I
      +500*h^2-2275*h^3+3440*h^4-1728*h^5.

This is exactly the `235II` elliptic quotient.  The map has degree five, as
expected from the subgroup index `[A5:A4]=5`.

## 4. The time form descends exactly

For the sphere Hamiltonian `H=Q_I`, direct Lie–Poisson differentiation gives

    dR_I/dt = -10*S_I.

Therefore

    dt = -dR_I/(10*S_I).

So the specific period sector studied in the dissertation is again the
canonical elliptic differential on the full rotation quotient.  The
genus-three intermediate curve contributes a Prym part, but the physical
polyhedral period lies in the elliptic factor.

## 5. A second maximal-subgroup quotient

Using the fivefold axis, the dihedral `D5` quotient can be written

    Y^2 =
      u * (
        4*u*(1-u)^5
        -(11*u^3-15*u^2+5*u-h)^2
      ).

For generic `h` this is squarefree of degree seven, hence another
genus-three curve.

So both natural maximal-subgroup routes checked so far give genus three,
not genus one.

## 6. What fails directly

The triangle–rectangle modular pullback has a zero of order two at its
triangular well `alpha=0`.

The icosahedral pullback has:

    order 3 at the C3 triangular well h=-5/27,
    order 5 at the C5 well h=1,
    order 2 at the C2 well h=0.

An analytic invertible energy change preserves these orders.  Therefore a
smooth unramified triangle-well to icosahedral-triangle-well identification
is impossible.  It would require a ramified relation with local exponent
`2/3`.

The direct equal-j fibre product is irreducible over Q and has bidegree

    (6,10)

in `(alpha,h)`.  Thus there is no hidden low-degree rational component
analogous to the octahedral energy relation.

## 7. What remains viable

This does not make the new model irrelevant to the icosahedral story.

The exact current diagram is

    icosahedral genus-25 sphere curve
             |
             | quotient by A4
             v
    genus-3 curve in (A,r)
             |
             | degree 5
             v
    235II elliptic quotient.

The triangle–rectangle curve uses the same `r,s` tetrahedral coordinates and
can represent the elliptic factor after an algebraic energy correspondence.
What is absent is the accidental genus-one collapse that occurred for the
octahedral subgroup chain.

The next useful tests are:

1. compute the Prym decomposition of the genus-three A4 quotient;
2. test whether its abelian-surface factor splits at special energies;
3. compare the triangle–rectangle elliptic curve with the `235II` factor
   under direct isomorphism and small-degree isogenies;
4. track the C3 and C5 cycles through the degree-five map;
5. test the `D3` maximal subgroup quotient;
6. search the free-mu plane family for a member whose quotient has the
   icosahedral `(2,3,5)` ramification pattern.

The direct octahedral-style answer is therefore “not yet”; the exact
icosahedral relation is one genus level higher, but it is substantial and
fully explicit.
