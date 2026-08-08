# Free-coefficient family

```text
INPUT:
    2H = p^2+q^2+c1*(q^3-3p^2*q)+c2*(q^2-3p^2)^2
    coefficient field K = Q(c1,c2)
    parameter polynomial ring R = K[alpha]

SYMBOLIC_PROFILE:
    build each homogeneous Jacobian map over K(alpha)
    evaluate (alpha,c1,c2) at nonsingular rational test values
    select generic pivot columns and rows
    solve the selected square system fraction-free over K[alpha]
    verify against every original row over K[alpha]

DISCOVER:
    reduce 2/(2H-alpha) and successive alpha derivatives
    stop at the first exact dependence
    clear content in Q[alpha,c1,c2]
    return the family operator and structured homotopy ledger

FALLBACK IF SYMBOLIC SWELL EXCEEDS BOUND:
    choose an interpolation grid of exact rational (c1,c2) values
    run the unchanged numeric engine at every point
    reject singular/rank-changing samples explicitly
    reconstruct coefficient polynomials/rational functions
    verify the reconstructed operator once over Q(c1,c2,alpha)
```

Numeric specialization is a fallback implementation strategy, not a proof by
sampling: the final reconstructed identity must still be checked symbolically.

## Current execution result

The direct symbolic route completes at order two, so interpolation was not
needed. Three fresh exact specializations were subsequently recomputed and
matched the symbolic operator. Keep the interpolation branch because larger
free-coefficient families may exceed the direct symbolic bound.
