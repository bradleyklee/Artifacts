# `PlaneCurveODE` pseudocode v0.2

```text
PlaneCurveODE(K(p,q), center, options):
    # Convention
    alpha := K
    VerifyMorseCenter(K, center)

    # Fast exact local data; useful for chart scoring and candidate discovery.
    series := ExactPeriodSeries(K, center, options.series_terms)

    # Prefer scalar affine/symplectic charts.
    for (x,y,transform) in CandidateCanonicalCharts(K):
        P(alpha,x,y) := Transform(K,transform)-alpha
        chart_data := AnalyzeProjection(P,y)
        # chart_data contains degree, leading coefficient, discriminant,
        # finite bad fibers, infinity branches, and a cost score.

    for chart in SortByCost(chart_data):
        result := PlaneChartToODE(chart, requested_form="period")
        if result.exact:
            result.series := series
            result := FactorAndRecertify(result)

            if options.require_action_certificate:
                action_result := ActionFiberToODE(K, result.operator)
                RequireSameOperatorOrExplainFactor(action_result,result)
                result.cross_certificates.append(action_result)

            return BuildReplayCertificate(result)

    # Canonical fallback retains lambda and all angular branches finitely.
    result := ActionFiberToODE(K, candidate_operator=None)
    if result.exact:
        return BuildReplayCertificate(FactorAndRecertify(result))

    # Optional common-frequency compression.
    if CommonHarmonicFrequencyExists(K):
        result := SymmetryCompressedToODE(K)
        if result.exact:
            CrossCheckAgainstUniversalBackend(result,K)
            return BuildReplayCertificate(FactorAndRecertify(result))

    return BoundedFailureRecord(all_attempts)
```

## Scalar chart backend

```text
PlaneChartToODE(chart):
    P(alpha,x,y) := 0
    A := Q(alpha,x)[y]/(P)

    ky := partial_y K
    kx := partial_x K

    delta_x := partial_x-(kx/ky)partial_y
    nabla_alpha := partial_alpha+(1/ky)partial_y
    omega := orientation_sign*2 dx/ky

    integral_basis_finite := IntegralBasis(A, finite_places)
    integral_basis_infty  := IntegralBasis(A, infinity_places)
    reducer := AlgebraicHermiteReducer(
        A,
        delta_x,
        integral_basis_finite,
        integral_basis_infty,
        pole_divisors=[leading_coefficient(P,y), discriminant_y(P)]
    )

    forms[0], primitive[0] := reducer.reduce(omega)

    for j from 1 to reducer.remainder_dimension:
        raw := nabla_alpha(forms[j-1])
        forms[j], step := reducer.reduce(raw)
        primitive[j] := nabla_alpha(primitive[j-1])+step

        relation := ExactDependence(forms[0..j], field=Q(alpha))
        if relation exists:
            L := relation_as_Ore_operator(relation)
            Xi := same_linear_combination(primitive[0..j])
            assert ReduceExactly(L(omega)-delta_x(Xi)*dx)==0
            return ExactResult(L,Xi,reducer.metadata)

    fail INTERNAL_DIMENSION_BOUND_VIOLATION
```

## Direct numerator recurrence for the current period form

```text
N[0] := 2
for j>=0:
    N[j+1] := K_y*partial_y(N[j])-(2j+1)*K_yy*N[j]

# Then nabla_alpha^j(2/K_y)=N[j]/K_y^(2j+1).
```

This recurrence can be used before the full integral-basis implementation and
as a regression check after it.
