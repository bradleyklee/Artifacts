# Wide-regime results

Date: 2026-08-02. Research owner: Bradley Klee. Unpublished; NO POACHING.

## Priority elliptic model

```text
alpha = 2H_ell
      = p^2+q^2+(q^3-3p^2q)+(q^2-3p^2)^2/4.
```

Both independent reducers find and exactly verify the same order-two operator:

```text
P0 = 3*alpha*(9*alpha-16)
P1 = 216*alpha^3-195*alpha^2-28*alpha+8
P2 = alpha*(3*alpha-2)*(4*alpha-1)*(9*alpha+4)
```

| measurement | Lairez-style | Klee bare |
|---|---:|---:|
| operator/reduction | 1.966 s | included below |
| certificate-aware | 2.932 s excluding setup | 7.654 s total |
| main exact-image rank | 53 of 55 | 20 exact columns, rank 20 |
| quotient dimension | projective class rows 2 | 8 |
| curve primitive | affine one-form verified | 43 terms, verified |

## Free-coefficient theorem candidate

For

```text
2H = p^2+q^2+c1*(q^3-3p^2q)+c2*(q^2-3p^2)^2
```

the extended port closes symbolically at order two over
`Q(c1,c2,alpha)`. Reduction takes 125.166 seconds; 103.752 seconds is the
large 53 by 53 fraction-free solve. The normalized operator has:

| coefficient | terms after expansion | alpha degree | c1 degree | c2 degree |
|---|---:|---:|---:|---:|
| P0 | 23 | 4 | 10 | 7 |
| P1 | 26 | 5 | 10 | 7 |
| P2 | 26 | 6 | 10 | 7 |

`P2` is stored in factored form and begins with `-alpha`; its remaining three
factors are explicit in `free_coefficients_symbolic_result.json`.

Fresh numeric recomputation at `(c1,c2)=(1,1/4),(1/2,1/8),(2,1/2)` agrees
exactly with symbolic specialization in all three cases. The bare Klee solver
also agrees and returns verified curve primitives. The must-have point has 43
primitive terms; the other two probes have 71, showing an additional
specialization-specific cancellation.

## Harmonic mixed-quartic grid

The comparison grid uses

```text
2H = p^2+q^2+c3*Re(q+i*p)^3+c4*Re(q+i*p)^4
tau = c3^2/c4.
```

All nine raw grid points are complete. Eight are order four; the tested
`tau=4` point is order two. Generic Lairez-style reductions have median 88.770
seconds and range 87.373--95.653 seconds. At `tau=2`, the bare Klee support search
has the sharp tested rectangular threshold `q_degree=21`: bounds 17, 19, and
20 fail; 21 succeeds. It returns the identical order-four operator and a
verified 487-term primitive in 133.262 seconds, versus 88.770--93.534 seconds
for the port.

An extreme `tau=32` Klee run also closes at `q_degree=21`, with the same
56-by-44 matrix shape, quotient dimension 12, and 487 primitive terms. It takes
144.534 seconds and agrees exactly with Pierre's operator (95.653 seconds).
Thus the support dimensions are stable across the tested generic coefficient
range even though coefficient size and wall time grow.

This grid separates two different quartic loci:

1. the non-harmonic `(q^2-3p^2)^2` family, generically order two;
2. the harmonic square family, generically order four with exceptional
   order-two coefficient ratios.

No general degree-only timing or order claim survives these tests.
