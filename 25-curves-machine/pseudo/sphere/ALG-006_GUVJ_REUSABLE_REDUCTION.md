# ALG-006 — Reusable G,U,V,J pole-lowering model

Purpose: replace a new one-shot exact-image solve at each order by reusable
Hermite--Ostrogradsky reduction operators.

```text
BuildGUVJ(E,basis_policy):
    R <- Q(alpha)[p,q]/(E-alpha)
    rho <- partial_p(E)
    D(f) <- rho*partial_q(f)-E_q*partial_p(f)
    dot_rho <- D(rho)

    M_rho     <- matrix of multiplication by rho
    M_dot_rho <- matrix of multiplication by dot_rho
    J         <- matrix of D
    G         <- [M_rho | -M_dot_rho]

    S <- exact inverse or certified right inverse of G
         on the declared reducible numerator subspace
    split S into block rows [U;V]

    assert G*[U;V] = identity on that subspace
    return rho,D,dot_rho,G,U,V,J
```

For a pole part `w/rho^(k+1)`:

```text
ReducePolePart(w,k,U,V,J):
    a <- U*w
    b <- V*w
    primitive_piece <- poly(b)/(k*rho^k)
    lower_numerator <- (U-(1/k)*J*V)*w

    assert
        w/rho^(k+1) * theta
        = lower_numerator/rho^k * theta
          + d(primitive_piece)

    return lower_numerator, primitive_piece
```

Apply this repeatedly to every derivative of `omega`; collect canonical
remainders and take their null space.  This model is algebraically equivalent
to ALG-002 because

```text
C_m = M_rho*J - m*M_dot_rho = G*[J; m*I].
```

Status: the pseudocode model is complete, but the current paired release uses
the proven one-shot ALG-002 implementation.  A major next engineering target is
to make ALG-006 reproduce both certificates from the same reusable reduction
operators.
