# Laurent-polynomial search plan

## Complete and open

Baseline complete: 1, 2, 3, 5, 7, 9.

Baseline open: 4, 6, 8, 10, 11.

New tacnode presentations:

- T0 is covered by the model-1 Laurent certificate.
- T1 has an exact order-three period equation and remains open.

## What is now excluded

For models 4, 8, and 10, the central-binomial palindromic product ansatz is
exhausted through degree 6. A 495-support, four-pair, rank-two symmetric box is
also exhausted. These are exact bounded failures, not global nonexistence
claims.

## Next search order

1. T1: allow a three-variable diagonal and an order-three recurrence. Do not
   force it into an order-two reflexive-polygon template.
2. Models 4, 8, and 10: enumerate five- and six-pair rank-two supports,
   nonsymmetric supports, and mutation-related templates. Reject from the known
   recurrence before computing many moments.
3. Models 6 and 11: first find a primitive normalization or parameterized
   family that removes the huge arithmetic scale from the coefficient solve.

## Acceptance rule

A candidate is retained only when all of the following hold:

```text
exact constant terms match a long period prefix;
a recurrence or differential equation is derived exactly;
the Laurent and plane equations agree after the stated rescaling;
an exact certificate is stored;
OEIS status is checked and recorded separately.
```
