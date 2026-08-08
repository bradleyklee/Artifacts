# PSEUDO-ANNIHILATOR-RELATIONS-001
## Score structural relations among annihilator coefficients

**Input**

```text
A = sum_{j=0}^r P_j(alpha) partial_alpha^j
```

with primitive polynomial coefficients.

**Output**

- exact relation signature;
- a simplicity score;
- candidate gauge, pullback, adjoint, or factor transformations.

```text
function AnalyzeAnnihilatorRelations(A)
    RemovePolynomialContent(A)
    FactorEveryCoefficient(A)

    signature.order <- Order(A)
    signature.degrees <- DegreeList(A)
    signature.supports <- MonomialSupports(A)
    signature.pairwise_gcd <- GCDMatrix(P_0,...,P_r)
    signature.leading_factorization <- Factor(P_r)
    signature.singularities <- RootsWithMultiplicities(P_r)

    relations <- empty

    for i,j in 0..r
        SearchSparseRelations(
            objects = [
                P_i, P_j,
                derivatives of P_i and P_j,
                alpha^k P_i and alpha^k P_j,
                factor multiples and quotients
            ],
            coefficient_bound = small integers,
            degree_bound = configured
        )
        Append(relations, exact null relations)

    signature.wronskian_log_derivative <-
        Simplify((P_{r-1} - Binomial(r,2)*Derivative(P_r))/P_r)

    signature.formal_adjoint_relation <-
        TestGaugeEquivalence(A, FormalAdjoint(A))

    signature.symmetric_power_drops <-
        TestSymmetricPowers(A)

    signature.exterior_power_drops <-
        TestExteriorPowers(A)

    signature.pullback_candidates <-
        MatchKnownLibraryAnnihilators(A)

    signature.apparent_singularities <-
        TestLocalExponentsAndMonodromyCandidates(A)

    signature.relation_score <- ScoreExactRelations(
        sparse_integer_relations,
        logarithmic_derivatives,
        repeated_factor_collisions,
        adjoint_equivalence,
        power_order_drops,
        known pullbacks
    )

    return signature
end function
```

The score is secondary evidence. Every reported relation must be saved as an
exact identity with zero residual.
