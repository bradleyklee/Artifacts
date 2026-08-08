# ALG-002 — Reductive derivative-class null-space certificate

Purpose: derive the first differential operator and its exact primitive directly
from the Hamiltonian, without supplying a period series or candidate operator.

## Derivative numerators

For

```text
omega = 2 dq/rho,
```

define

```text
N[0] = 2
N[j+1] = rho * partial_p(N[j])
         - (2*j+1) * N[j] * partial_p(rho)
```

so that

```text
partial_alpha^j(omega) = N[j] dq / rho^(2*j+1)
```

on the energy curve.  At target order `r`, convert every derivative to the
common denominator `rho^(2*r+1)`:

```text
W[j] = ReduceCurve(N[j] * rho^(2*(r-j)), E-alpha)
```

## Exact-image map

Set

```text
m = 2*r - 1
D(V) = rho*partial_q(V) - E_q*partial_p(V)
dot_rho = D(rho)
C_m(V) = ReduceCurve(rho*D(V) - m*dot_rho*V, E-alpha)
```

Then

```text
d(V/rho^m) = C_m(V) dq / rho^(m+2).
```

Since `m+2=2*r+1`, exact images and derivative classes have the same
denominator.

## Basis-free null-space derivation

```text
ReductiveNullspaceCertificate(E, max_order, basis_growth_policy):
    rho <- partial_p(E)
    certify D(E-alpha)=0

    N[0] <- 2

    for r = 1..max_order:
        extend N through N[r]
        W <- columns W[0],...,W[r]

        source_basis <- BasisGrowthPolicy(E, r, certified_symmetries)
        C <- columns C_m(b) for b in source_basis

        ambient_basis <- sorted union of actual supports of C and W
        encode C and W in ambient_basis over Q(alpha)

        rank_C  <- ExactRank(C)
        rank_CW <- ExactRank([C | W])
        relation_dimension <- (r+1) - (rank_CW-rank_C)

        if relation_dimension = 0:
            record NO_RELATION_IN_DECLARED_FILTRATION
            continue

        if relation_dimension > 0:
            # Use [C|-W] so Cv=WP directly.
            Z <- ExactNullspace([C | -W])
            select z=[v;P] with top derivative P[r] != 0
            P <- ClearDenominatorsContentAndSign(P)
            rescale v by the same scalar

            assert C*v = W*P exactly
            operator A <- Sum_j P[j](alpha) partial_alpha^j
            primitive Xi <- Poly(source_basis,v) / rho^(2*r-1)

            return A, Xi, ranks, supports, nullspace_trace

    return NO_RELATION_IN_SEARCHED_ORDERS
```

The equality `C*v=W*P` is exactly the certificate

```text
A(omega) = d(Xi).
```

No pivot rows are mathematically required.  The only guessed object is a finite
source-basis policy; ALG-004 determines whether that finite search is exhaustive
or merely bounded.
