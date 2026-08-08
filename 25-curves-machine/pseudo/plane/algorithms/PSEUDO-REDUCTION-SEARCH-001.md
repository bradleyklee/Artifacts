# PSEUDO-REDUCTION-SEARCH-001
## Search the reduction space for one Hamiltonian

**Input**

- polynomial Hamiltonian `H(p,q;theta)`;
- energy parameter `alpha = 2H`;
- candidate algorithm record `Q`;
- derivative/order/pole bounds.

**Output**

- annihilator `A`, certificate `Xi`, and reduction trace; or
- the first exact obstruction and last valid exact object.

```text
function SearchReductionSpace(H, alpha, Q, bounds)
    H0 <- NormalizeHamiltonian(H, Q.normalization)
    charts <- GenerateCharts(H0, Q.chart_policy)

    for chart in RankCharts(charts, Q.chart_score)
        algebra <- BuildAlgebra(H0, alpha, chart, Q.algebra_policy)

        if not VerifyDefiningRelations(algebra)
            RecordFailure("algebra-construction", chart)
            continue

        omega <- BuildPeriodDifferential(H0, algebra, Q.form_policy)
        poles <- AnalyzePolesAndInfinity(omega, algebra, Q.pole_policy)
        reducer <- BuildReducer(algebra, poles, Q.reduction_kernel)

        remainders <- empty
        primitives <- empty

        for j from 0 to bounds.maximum_derivative_order
            omega_j <- ParameterDerivative(omega, j, algebra)
            (exact_j, remainder_j, trace_j) <-
                ReduceModuloExactDifferentials(omega_j, reducer)

            SaveDerivativeAndReduction(j, omega_j, exact_j, remainder_j, trace_j)
            primitives[j] <- exact_j
            remainders[j] <- Coordinates(remainder_j)

            relation <- FirstExactDependence(remainders)
            if relation exists
                A <- NormalizeAnnihilator(relation, alpha)
                Xi <- AssembleCertificate(A, primitives)

                if VerifyTelescopingIdentity(A, omega, Xi, algebra)
                    (Amin, Ximin) <- SearchAndRecertifyRightFactors(A, Xi)
                    signature <- AnalyzeAnnihilatorRelations(Amin)
                    return ExactSuccess(Amin, Ximin, signature, full_trace)

        RecordFailure(
            "no-dependence-within-bound",
            last_valid_object = Last(remainders)
        )

    return FailureWithDiagnostics()
end function
```
