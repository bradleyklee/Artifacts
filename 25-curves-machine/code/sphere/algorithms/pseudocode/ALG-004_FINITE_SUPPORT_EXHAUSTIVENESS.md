# ALG-004 — Finite-support exhaustiveness

Purpose: distinguish a bounded matrix search from a proof that no relation was
missed outside the chosen monomial support.

```text
ProveFiniteStopping(E, r, symmetry_sector, filtration):
    compute the leading action of C_m on monomials of filtration weight n
    derive its symbol determinant or diagonal coefficient S_r(n)

    resonant_weights <- integer roots of S_r(n)

    prove:
        for n > stopping_bound(r), S_r(n) is invertible
        every source monomial of weight n can be eliminated using its leading image
        lower-weight correction terms stay inside the filtration

    return stopping_bound(r), resonant_weights, proof_trace
```

Then the order search is exhaustive when the source basis contains every allowed
monomial through `stopping_bound(r)`.

For square-hexagon the derived symbol is

```text
S_r(n) = 419904
         * (n-(8*r-3))
         * (n-(8*r-4))
         * (n-(6*r-3)).
```

The computation uses all symmetry-allowed source monomials through weight
`8*r-3`.  Therefore the zero relation dimensions at orders 1, 2 and 3 are
finite proofs, not truncated experiments.

For triangle-square the current order-one exclusion is only bounded through the
reported q-degree.  The order-two identity is exact in its declared source
space, but an analogous general stopping proof remains to be written.
