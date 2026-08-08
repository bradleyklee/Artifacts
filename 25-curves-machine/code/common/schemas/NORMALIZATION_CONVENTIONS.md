# Shared normalization conventions

- New shared interfaces use `H_p` for the partial derivative/function. `E_p` is not used because it is reserved as a constant in this research program.
- A plane model declares whether the stored polynomial is `H` or `E=2H`; adapters must not infer this silently.
- Differential operators store coefficients from derivative order zero upward.
- Exact operators are divided by their common polynomial/content factor when this is meaningful, and the remaining scalar convention is recorded.
- Primitive records state the exact identity being checked, for example `A(omega)=d(Xi)`.
- Sphere records declare the sphere constraint, axis/chart choice, and energy normalization.
- Modular and numerical outputs are never labeled exact.
