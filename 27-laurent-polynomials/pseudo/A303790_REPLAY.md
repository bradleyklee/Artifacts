# A303790 exact replay pseudocode

## Hamiltonian certificate

1. Define `K = p^2 + q^2 + p^3 + q^3` and the stated second-order energy operator.
2. Define the supplied rational certificate `Xi = V / K_p^3`.
3. Differentiate explicitly at fixed `q` using `(1/K_p) partial_p`.
4. Form the difference between the operator applied to `2/K_p` and the derivative of `Xi` along `K=E`.
5. Clear denominators and divide the numerator polynomial by `K-E` as a polynomial in `p`.
6. Accept only when the remainder is exactly zero.

## Laurent certificate

1. Form the two factors `P(w)` and `Q(y)` of the integral Laurent polynomial.
2. Verify the supplied rational identity for `R(n,y)` by explicit differentiation and denominator cancellation.
3. Multiply by `Q(y)^n` and take the bracket constant term. The derivative term contributes zero.
4. Combine the resulting recurrence for `[Q(y)^n]_0` with the exact binomial ratio for `[P(w)^n]_0`.
5. Normalize the recurrence by explicit factor cancellation.
6. Generate coefficients recursively and verify the first ten independently by direct Laurent expansion.
7. Translate the recurrence to the differential equation and check the coefficient residuals.
8. Substitute `E=32t` in the Hamiltonian operator and require exact equality with the Laurent operator.

No generic simplification routine is used. Every normalization step is named and checked.
