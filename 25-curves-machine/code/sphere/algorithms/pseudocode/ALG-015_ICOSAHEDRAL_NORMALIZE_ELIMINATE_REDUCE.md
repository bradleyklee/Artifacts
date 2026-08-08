# ALG-015 — Icosahedral normalize, eliminate, reduce

```text
input the published fivefold-axis surface H_raw(lambda,phi)
record its three critical energies from the leading polynomial factors
derive or fit the affine energy map sending them to the Chapter-4 convention

alpha := (16*H_raw+5)/21
h1 := 11*lambda^6 - 15*lambda^4 + 5*lambda^2
h2 := 2*lambda*(1-lambda^2)^(5/2)
H := h1 + h2*cos(5*phi)

P(lambda,alpha) := -25*((alpha-h1)^2-h2^2)
assert P is a degree-12 polynomial in lambda

omega[0] := d_lambda/sqrt(P)
for k = 0,1,2:
    differentiate omega[k] in alpha
    divide out higher powers using z^2=P
    subtract exact lambda derivatives
    store the 11 polynomial-basis coefficients as a matrix column

find the first nullspace relation
reconstruct the discarded exact terms as Xi
normalize operator and Xi together
verify operator(omega)=d_lambda(Xi) exactly
compare with Chapter 4 only after zero residual
write every raw normalization, failed comparison, matrix, timing and closure to JSON
```

The raw Harter--Weeks normalization also closes at order two, but its operator has singular factors at `1,-5/9,-5/16`. That is valid data, not a failed algorithm. The affine energy adapter sends them to `1,-5/27,0` and converts the result to the dissertation convention.
