# Plane scan pseudocode

## Input

The 56 allowable four-singular-fiber configurations with nonconstant J are a
historical classification input. The plane calculations below are independent
checks inside two explicitly stated Hamiltonian families.

## Cubic family

```text
E = p^2 + q^2 + a p^3 + b p^2 q + c p q^2 + d q^3.

Compute c4(E), c6(E), and Delta(E)=c4(E)^3-c6(E)^2 exactly.
Use their degree deficits to classify the fiber at infinity.
Reject incompatible target configurations.
For every surviving target, substitute an exact witness.
Factor Delta exactly.
At every finite factor and at infinity, compute valuations of c4, c6, Delta.
Classify the fibers and require Euler total 12.
```

The degree profile forces the infinity fiber to be IV*, III*, or II*. The scan
finds three exact configurations.

## Two-point quartic family

```text
E = p^2 + q^2 + L2 L1 + mu L2^2,
L2 = q^2-r p^2,
L1 = sqrt(U) p + sqrt(V) q.

Project from a fixed double point at infinity.
Compute the residual binary quartic and its exact invariants.
Classify finite fibers and infinity as above.
```

The nondegenerate degree profile forces an I_n* fiber at infinity. The scan
finds eight additional configurations.

## Acceptance rule

A model is public only when it has an explicit Hamiltonian, exact discriminant
factorization, exact fiber classification, Euler total 12, and a JSON audit
record. A period model needs exact coefficients and a checked differential
equation. A complete isoperiodic model additionally needs independent exact
Hamiltonian and Laurent certificates for the same normalized germ.
