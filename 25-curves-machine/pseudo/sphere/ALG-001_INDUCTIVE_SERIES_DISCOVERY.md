# ALG-001 — Inductive exact-series discovery

Purpose: generate exact period data, guess candidate differential operators,
and provide independent checks.  This is discovery, not the final proof.

```text
InductivePeriodDiscovery(E_in_action_angle, series_order, search_boxes):
    # E(lambda,phi) has harmonic leading term lambda.
    # alpha is the energy parameter E=2H.

    lambda_series(alpha,phi) <- FormalSeriesReversion(
        alpha = E(lambda,phi),
        solve_for = lambda,
        order = series_order + 1
    )

    action_series I(alpha) <- ConstantTerm_phi(lambda_series)
    period_series T(alpha) <- derivative_alpha(I(alpha))

    assert all coefficients are exact rationals/algebraic numbers

    for (operator_order r, coefficient_degree d) in search_boxes:
        # Find polynomials P_j(alpha), degree <= d, not all zero.
        build homogeneous linear system from
            Sum_{j=0}^r P_j(alpha) * derivative_alpha^j(T(alpha)) = O(alpha^N)
        relation_space <- ExactNullspace(system)

        for relation in relation_space:
            A <- PrimitiveIntegerNormalize(relation)
            verify A(T)=0 on coefficients not used for fitting
            record A if verification passes

    return exact_series, verified_candidate_operators
```

Required safeguards:

```text
- Fit and validation coefficient ranges must be disjoint.
- The number of available equations must exceed the number of unknowns.
- Candidate operators are not certificates until ALG-002/ALG-005 succeeds.
- Record failed search boxes as bounded failures, not nonexistence proofs.
```
