# Direct addition-law decision test for maximal plane quartics

## Correction

The earlier package mostly verified known cubic/Edwards formulas.  It did not
supply a complete decision test.  This package replaces that with a direct
plane-quartic test in the original Hamiltonian coordinates.

Write the unrestricted quartic Hamiltonian as

```text
H(p,q) = H4(p,q)+H3(p,q)+H2(p,q)+H1(p,q)+H0
```

and homogenize the generic level curve:

```text
F(p,q,z;alpha)
 = H4 + z H3 + z^2 H2 + z^3 H1 + z^4(H0-alpha).
```

The time differential is

```text
omega = dq / H_p.
```

No Weierstrass conversion is used.

## Exact existence test on the original quartic

For an irreducible complete curve, a rational binary group law with an
identity can exist on the normalization only when its geometric genus is one.
For a plane quartic the arithmetic genus is three, so

```text
g = 3 - sum(delta_P).
```

The direct test is therefore:

1. Find the projective singularities of `F=0`.
2. Resolve them by blowups and sum their delta invariants.
3. If `g != 1`, declare exactly:

   ```text
   no elliptic binary addition law exists on the original quartic.
   ```

4. If `g = 1`, test whether `omega=dq/H_p` is regular on the normalization.
   For the two-node stratum below, the affine numerator `1` homogenizes to the
   adjoint line `z=0`, so regularity is automatic.
5. Find a rational base point/branch `O` over the coefficient field.
6. If `O` exists, derive the law directly by adjoint-conic residual
   intersection and verify

   ```text
   m^* omega = omega_1 + omega_2.
   ```

A genus-one curve with no rational point is a torsor.  It has a rational
ternary law `P-Q+R`, but no binary law over that field.  Proving absence of a
rational point can often be done by a local obstruction or descent, but there
is no presently available unconditional algorithm guaranteed to terminate on
every genus-one curve over Q or every symbolic coefficient field.  This is the
arithmetic blocker, not a deficiency of the geometric test.

## Maximal-form singularity test

In the chart `p=1`, put

```text
A(t)=H4(1,t),
B(t)=H3(1,t).
```

The singular directions at infinity are exactly the roots of

```text
gcd(A(t), A'(t), B(t)).
```

For generic unrestricted coefficients this gcd is one.  Hence the generic
plane quartic is smooth at infinity, has genus three, and has no binary
elliptic addition law on the original curve.

This also corrects an earlier overstatement: a generic even quartic may have
an elliptic quotient carrying the period differential, but its original plane
quartic is generically genus three and does not itself admit a binary group
law.

## A large explicit genus-one stratum

Let

```text
H4 = k Q2(p,q)^2,
H3 = Q2(p,q) L1(p,q),
```

where `Q2` is a squarefree binary quadratic and `L1` is linear.  At either root
`r` of `Q2(1,t)`, the local tangent cone is

```text
k Q2'(r)^2 xi^2
 + Q2'(r)L1(r) xi z
 + H2(1,r) z^2.
```

Its discriminant is

```text
Q2'(r)^2 * (L1(r)^2 - 4 k H2(1,r)).
```

If this is nonzero at both roots, the projective quartic has two ordinary
nodes at infinity.  Their total delta is two, hence the normalization has
geometric genus one.

At a rational root `r`, a rational normalization branch exists when

```text
L1(r)^2 - 4 k H2(1,r)
```

is a square in the base field.  This gives an immediate rational identity
branch and therefore a binary addition law.

## Direct derivation by conics

For a quartic with two ordinary nodes `N1,N2` and a rational identity `O`, the
law can be derived without guessing it:

1. Construct the unique conic through `N1,N2,O,P,Q`.
2. Its eighth intersection divisor with the quartic has one residual point
   `R`, since each node contributes two branch intersections.
3. Define the residual involution `sigma(P)=R(P,O)`, using the tangent limit
   when `O` is repeated.
4. Then

   ```text
   P (+) Q = sigma(R(P,Q)).
   ```

This follows solely from divisor equivalence of conic sections.  Solving the
linear conic equations and one resultant produces rational coordinates.

## Computed benchmark: Edwards quartic

For

```text
x^2+y^2 = 1+d x^2 y^2,
O=(0,1),
```

the projective quartic has two rational nodes at infinity.  The code constructs
rather than inserts the conic

```text
a*x*y + b*x + c*(y-1)=0
```

through the nodes, `O`, `P`, and `Q`, obtains the residual point `R`, and finds
that the residual involution is `(x,y)->(x,-y)`.  Simplification gives

```text
X = (x1*y2+y1*x2)/(1+d*x1*x2*y1*y2),
Y = (y1*y2-x1*x2)/(1-d*x1*x2*y1*y2).
```

This was not preloaded into the construction.  Independently, a
three-parameter rational ansatz constrained by curve closure and the time
 differential gives the Groebner basis

```text
cpar-1, epar+1, gpar+1,
```

which uniquely recovers the same coefficients.  Exact reduction modulo the
two input curve equations verifies curve closure and both components of

```text
m^* omega = omega_1 + omega_2.
```

## Computed decisions

The blowup classifier returns:

```text
generic maximal quartic:       g=3  -> exact NO on original curve
generic even quartic:          g=3  -> exact NO on original curve
Edwards two-node quartic:      g=1  -> law exists; rational branches found
mechanical quartic:            g=1  -> geometrically elliptic; base field test remains
Edwards plus generic cubics:   g=3  -> cubic terms destroy the two nodes; exact NO
```

For the mechanical example the sole infinity singularity has delta two.  Its
second blowup tangent cone is `u^2+w^2`, so the infinity branches require `i`
over the generic rational coefficient field.  A binary law still exists after
a rational point is supplied in a specialization or after extending the base
field.

## What remains

The two-node branch is now a real derivation algorithm, not a formula lookup.
The next missing implementation is the corresponding adjoint-conic condition
for one-delta-two singularities such as tacnodes.  The genus calculation is
already complete for the tested tacnode; only automatic construction of the
fixed infinitely-near conic conditions remains.
