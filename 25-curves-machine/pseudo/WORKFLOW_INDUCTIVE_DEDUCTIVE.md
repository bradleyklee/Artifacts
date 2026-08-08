# Inductive / deductive operating loop

## State machine

```text
REGISTERED_GEOMETRY
  -> DATA_GENERATION
  -> PATTERN_CANDIDATE
  -> DEDUCTIVE_REDUCTION
  -> RAW_CERTIFICATE
  -> CRYSTALLINE_SUCCESS
  -> PRETTY_CERTIFICATE
  -> REGRESSION_COVERED
```

At any stage, execution may instead produce:

```text
BOUNDED_FAILURE       exact exclusion within a declared search box
METHOD_GAP            no registered algorithm currently applies or closes
TIMEOUT               reproducible time-limit record
MEMORY_OVERFLOW       reproducible memory-limit record
BUG                    implementation defect with failing regression
ENVIRONMENT_BLOCKER   required executable/dependency unavailable
```

Only `TIMEOUT` and `MEMORY_OVERFLOW` count as acceptable final limits for the
ultimate coverage target. The other failure states remain active work.

## Inductive mode

1. Register the exact geometry and conventions.
2. Generate exact or modular period data.
3. Record every explored order/degree/support box, not just the winning point.
4. Compare signatures, ranks, singular values, relation shapes, and scaling.
5. Formulate a candidate operator, bound, certificate shape, or algorithmic
   hypothesis.
6. Store the data and hypothesis before switching modes.

## Deductive mode

1. Select the candidate relation or structural claim.
2. Apply exact reduction, Hermite/Griffiths-Dwork style reduction, quotient
   reduction, creative telescoping, or another registered method.
3. Reconstruct the operator and exact primitive/certificate.
4. Verify the identity independently from serialized data.
5. Emit a raw certificate even when the attempt fails or times out.
6. Update coverage and algorithm success/failure notes.

## Promotion rule

A result becomes `CRYSTALLINE_SUCCESS` only when:

- the model and normalization are unambiguous;
- the operator is canonicalized;
- the certificate identity verifies exactly;
- minimality or the precise weaker claim is stated honestly;
- replay code and raw data are present;
- the result teaches a reusable structural lesson.

Only then should a pretty-print certificate be built.
