# Current algorithm-space note: square–hexagon search

## Research target

Find explicit even quartic–sextic Hamiltonians whose period annihilator `A`
has unusually simple coefficient relations, while improving the ability to
certify a generic particular parameter value.

## Active candidate algorithms

```text
PSEUDO-SQUARE-HEXAGON-STRATA-001
    proposes parameter strata from exact series and relation signatures

PSEUDO-ANNIHILATOR-RELATIONS-001
    measures coefficient syzygies, self-adjoint forms, factor collisions,
    adjoint relations, and symmetric/exterior-power drops

PSEUDO-REDUCTION-SEARCH-001
    attempts exact reconstruction and certification in several coordinates

PSEUDO-META-SEARCH-001
    compares failures and mutates the reducer
```

## Required next experiment

```text
1. Reproduce the saved square–hexagon exact coefficient stream.
2. Reproduce every modular rank result before extending it.
3. Recover one exact annihilator A and verify it on unused coefficients.
4. Print its exact relation signature.
5. Attempt certification in the compressed algebra
       G(alpha,lambda,c)=0, y^2=1-c^2.
6. Record the first failed reduction stage.
7. Mutate only that algorithmic stage.
8. Rerun pure-square, pure-hexagon, triangle-square, and square-hexagon controls.
```

## Learning rule

A parameter value is useful in two different ways:

```text
nice stratum:
    coefficient relations in A become simpler

diagnostic stratum:
    it isolates a failure of one reduction algorithm and thereby suggests
    the next pseudocode mutation
```

Both are retained. The project is not only cataloging curves; it is learning
which reduction algorithm should be used or constructed for each curve class.
