# Reductive period algorithm for quartic Hamiltonians

## Scope

Input is a rational polynomial Hamiltonian `E(p,q)=2H(p,q)` of degree at most
four, with a regular small oval on `E=alpha`.  No reflection symmetry is
required.

The strongest uniform branch assumes the homogeneous quartic part `F4` is
squarefree.  Degenerate infinity is detected and routed to a coefficient-
specific band-symbol calculation.

## Coordinate preparation

```text
PrepareQuartic(E):
    F4 <- homogeneous degree-four part of E
    if F4 = 0:
        route to lower-degree algorithm

    choose rational vector (A,C) with F4(A,C) != 0
    complete (A,C) to M=[[A,B],[C,D]] in SL(2,Q)
    replace (p_old,q_old) by (A*p+B*q, C*p+D*q)

    # Now coefficient a40 of p^4 is nonzero and reduction modulo E-alpha
    # has the fixed residue basis 1,p,p^2,p^3.
    return transformed E
```

## Derivative classes

```text
rho <- partial_p E
N[0] <- 2
for j = 0,1,...:
    N[j+1] <- rho*partial_p N[j] - (2*j+1)*rho_p*N[j]

# partial_alpha^j omega = N[j] / rho^(2*j+1) dq
```

At candidate order `r`, put every derivative over `rho^(2*r+1)`:

```text
W[j] <- NormalForm( N[j]*rho^(2*(r-j)), E-alpha )
```

## Exact-image map

For `m=2*r-1`, define

```text
D(V)       <- rho*partial_q V - E_q*partial_p V
rho_dot    <- rho*E_pq - E_q*E_pp
C_r(V)     <- NormalForm( rho*D(V) - m*rho_dot*V, E-alpha )
```

Then

```text
C_r(V) / rho^(2*r+1) dq = d( V/rho^(2*r-1) )
```

on the energy curve.

## Uniform squarefree-at-infinity bound

Write

```text
F4 = a*p^4+b*p^3*q+c*p^2*q^2+d*p*q^3+e*q^4,
Delta4 = discriminant(F4),
```

with `a != 0`.  On total-weight `n`, the associated-graded exact-image map
has determinant

```text
Delta4^2/a^4 * (n-(6*r-3))^4.
```

Therefore, if `Delta4 != 0`, every source weight above

```text
B_r = 6*r-3
```

reduces.  The exhaustive primitive source is

```text
P_r = span{p^i*q^j : 0 <= i <= 3, i+j <= B_r}.
```

For `r>=1`:

```text
source columns <= 4*B_r-2 = 24*r-14
ambient rows   <= 4*(B_r+5)-2 = 24*r+6
combined cols  <= 25*r-13
primitive pole = rho^(2*r-1)
```

The resonant weight `n=6*r-3` is retained in the finite source space; only
weights strictly above it are eliminated recursively.

## Null-space derivation

```text
QuarticCertificate(E):
    E <- PrepareQuartic(E)
    mu <- DimensionOfJacobianAlgebra(E_p,E_q)
    r_max <- min(mu, 9)  # Bezout bound for a quartic with isolated critical points

    for r = 1,...,r_max:
        if Discriminant(F4) != 0:
            B <- 6*r-3
        else:
            B <- CoefficientSpecificBandSymbolBound(E,r)

        labels <- {(i,j): 0<=i<=3 and i+j<=B}
        C <- columns C_r(p^i q^j)
        W <- columns W[0],...,W[r]

        K <- Nullspace([C | W])
        relation_rows <- vectors in K with nonzero W-part

        if relation_rows is empty:
            record exact no-relation result at order r
            continue

        choose relation with nonzero highest derivative
        clear Q(alpha) denominators and polynomial content
        recover operator P[0..r] from W-part
        recover primitive coefficients from C-part
        verify literal sparse identity modulo E-alpha
        return operator, primitive, rank trace, bound proof

    return NO_RELATION_WITHIN_JACOBIAN_BOUND
```

## Degenerate infinity fallback

When `Delta4=0`, the top `4x4` symbol is singular.  This does not imply that
the period is unsolvable; the radial quartic example is a successful case.
Use the full degree-band decomposition of `C_r`:

```text
C_r = S5(n) + S4(n) + S3(n) + S2(n) + S1(n),
```

where `Sk` raises total degree by `k`.  Increase a source-degree window and
form its polynomial band matrix over `Q(n,alpha)`.  The first nonzero maximal
minor gives a coefficient-specific resonance polynomial.  A bound above its
largest real root is exhaustive.  If no finite full-rank band appears, enlarge
the pole grammar (for example include a divisor at infinity) or use projective
Griffiths--Dwork reduction.

This fallback is algorithmic, but the current implementation is not yet as
complete as the squarefree branch.
