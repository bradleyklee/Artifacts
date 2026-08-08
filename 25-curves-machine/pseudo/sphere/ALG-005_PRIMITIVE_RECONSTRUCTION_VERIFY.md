# ALG-005 — Primitive reconstruction and verification

Purpose: turn the null vector into a release certificate and check it without
relying on the matrix solve that produced it.

```text
ReconstructAndVerify(E,r,source_basis,P,v):
    rho <- partial_p(E)
    m <- 2*r-1

    V <- Sum_i v[i](alpha) * source_basis[i](p,q)
    Xi <- V/rho^m
    A  <- Sum_j P[j](alpha) * partial_alpha^j

    # Independent sparse identity check.
    lhs_numerator <- CommonDenominatorNumerator(A(2*dq/rho), rho^(2*r+1))
    rhs_numerator <- rho*D(V) - m*D(rho)*V

    lhs_reduced <- ReduceCurve(lhs_numerator,E-alpha)
    rhs_reduced <- ReduceCurve(rhs_numerator,E-alpha)

    assert lhs_reduced-rhs_reduced = 0

    # Normalization and optional reduction audits.
    divide common content from P
    test gcd(P[0],...,P[r]) = 1
    test whether V is divisible by rho modulo E-alpha

    serialize:
        operator polynomial coefficient arrays
        primitive coefficient blocks
        expanded alpha,p,q terms
        source and ambient bases
        rank/nullspace trace
        hashes and replay log

    return certificate_payload
```

The independent sparse check is essential: matrix equality checks the chosen
finite representation, while curve reduction checks the literal differential
identity in `Q(alpha)[p,q]/(E-alpha)`.
