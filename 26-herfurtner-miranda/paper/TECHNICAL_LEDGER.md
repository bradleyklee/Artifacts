# Technical ledger

## Baseline

The release verifies 3 harmonic cubics and 8 quartics with two fixed nodes at
infinity. All 11 have 31 exact period coefficients and checked equations. Six
baseline models, 1, 2, 3, 5, 7, and 9, have exact Laurent certificates.

## One-tacnode quartics

The solved family is

```text
2H=p^2+q^2+2s p^2q+v p q^2+w q^3
   +s^2 p^2q^2+s v p q^3+c q^4.
```

At `[1:0:0]` its tangent cone is a square and the cubic term vanishes on the
tangent. Projection gives

```text
Y^2=(v^2-4c)x^4-4w x^3-4x^2+4E.
```

With `A=v^2-4c`, normalized invariants are

```text
c4=1+3AE,
c6=1-(9A+27w^2/2)E.
```

For generic `A`, infinity is `III*` and the three finite discriminant roots are
`I1`. This produces additional plane presentations of an existing fiber
configuration.

The Hamiltonian time form becomes

```text
dx / ((1+s*x)*sqrt(Q)).
```

For `s=0` it is holomorphic. For `s!=0` it is generally third kind, which
explains why the sheared example T1 has an order-three period equation although
the underlying elliptic family has an order-two holomorphic equation.

## Laurent bounded exclusions

For baseline models 4, 8, and 10, an exhaustive integer search excludes the
palindromic product class

```text
F=((1+w)^2/w)*(g0+sum_{k=1}^d gk(z^k+z^-k))
```

for `d=5,6`: every candidate fails by the fourth reduced moment. A separate
495-support rank-two box fails already at the third reduced moment. Exact counts
and scope warnings are in `examples/data/`.

## OEIS truth boundary

Baseline model 2 is exactly OEIS A303790. The other stored raw integer prefixes,
and T1, produced no exact-prefix match in the searches recorded on 2026-08-05.
This is not a proof of absence under another normalization or transform.

## Remaining geometry boundary

The tacnode stratum is not the whole quartic boundary. Delta-two unibranch
singularities, degenerate tacnodes, and rational-presentation coverage still
need explicit classification before a global quartic completeness claim is
made.
