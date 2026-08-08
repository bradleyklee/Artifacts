# PSEUDO-META-SEARCH-001
## Search algorithm space by using an example portfolio

**Input**

- bounded Hamiltonian family `F`;
- portfolio `C = C_known union C_transfer union C_unknown`;
- pseudocode library `P`;
- exact resource budget `B`;
- scoring rules `Score`.

**Output**

- Pareto-ranked candidate algorithms;
- exact success bundles;
- obstruction records;
- new or revised pseudocode entries.

```text
function SearchAlgorithmSpace(F, C, P, B, Score)
    Queue <- SeedCandidates(F, P)
    Archive <- empty
    Evidence <- empty

    while Queue is not empty and BudgetRemains(B)
        Q <- SelectCandidate(Queue, Archive, Evidence, Score)
        Emit("candidate-start", Q.id)

        for case in SchedulePortfolio(C, Q)
            result <- ExecuteCandidate(Q, case, B.case_limit)

            SaveReductionTrace(Q, case, result)
            UpdateEvidence(Evidence, Q, case, result)

            if result.exact_certificate_verified
                features <- ExtractSuccessfulMechanism(result)
                relations <- AnalyzeAnnihilatorRelations(result.A)
                SaveSuccessBundle(case, Q, features, relations)

            else
                obstruction <- ClassifyFirstObstruction(result)
                SaveFailureBundle(case, Q, obstruction)

        score <- ScoreCandidate(Q, Evidence)
        Archive <- Archive union {(Q, score)}

        mutations <- ProposeMutations(
            Q,
            SuccessfulMechanisms(Evidence, Q),
            CommonObstructions(Evidence, Q),
            NearestPrecedents(P, Q)
        )

        for Qnew in mutations
            if not EquivalentToArchivedCandidate(Qnew, Archive)
                WriteLanguageNeutralPseudocode(Qnew)
                Queue <- Queue union {Qnew}

    return ParetoFrontier(
        Archive,
        objectives = [
            exact_coverage,
            certificate_coverage,
            annihilator_relation_score,
            simplicity,
            runtime,
            memory,
            diagnostic_value
        ]
    )
end function
```

A candidate is not rewarded merely for producing a guessed annihilator.
Certificate coverage and replayable reduction traces dominate the score.
