# One all-orders algorithm

```text
DERIVE(F)
  F <- normalize exact bivariate Laurent input
  terms <- exact constant terms of successive powers of F

  repeat with expanding order and shift windows
    build the exact recurrence matrix for t^s theta^j
    for each exact nullspace relation using the newest derivative
      normalize the operator
      keep it only if unused terms satisfy it exactly
      go to CERTIFY

CERTIFY
  write every theta derivative over one common power of rho = 1-tF
  repeat with expanding Laurent support
    build all pole layers of the Euler-divergence witness
    solve the coefficient identity directly over Q(t) or Q(i)(t)
    if inconsistent, enlarge the support and continue
    replay the complete symbolic identity exactly
    replay the recurrence on the computed terms exactly
    return the operator, witness, terms, and search statistics
```

There is no order-two production branch and no witness-degree reconstruction
bound. Optional command-line limits are resource controls only. Exhausting one
is reported as an unfinished search, never as proof that no certificate exists.
