# ALG-003 — Explicit quotient matrix audit

Purpose: expose the small reduced derivative matrix, as in the original
triangle-square calculation.

Given the matrices `C` and `W` from ALG-002:

```text
ExplicitQuotientAudit(C,W,row_policy):
    assert rank(C) = number_of_columns(C)

    pivot_rows <- SelectIndependentRows(C,row_policy)
    C_piv <- C[pivot_rows,:]
    W_piv <- W[pivot_rows,:]

    certify det(C_piv) != 0 in Q(alpha)
    X <- inverse(C_piv) * W_piv

    R_full <- W - C*X
    assert R_full[pivot_rows,:] = 0

    quotient_rows <- all_rows minus pivot_rows
    R <- R_full[quotient_rows,:]

    relation_space <- ExactNullspace(R)
    P <- normalized vector with nonzero top derivative
    v <- X*P

    assert R*P = 0
    assert C*v = W*P

    return R, P, v, pivot_rows, quotient_rows
```

Interpretation:

```text
C : large exact-image solve
R : skinny matrix of derivative classes modulo exact forms
ker(R) : differential operators
X*P : primitive numerator coefficients
```

Current dimensions:

```text
triangle-square: C=32x20, R=12x3
square-hexagon:  C=53x42, R=11x5
```
