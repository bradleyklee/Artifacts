# Square–hexagon progress after the merged certificate

Date: 2026-08-02  
Research owner: Bradley Klee  
Privacy: unpublished research; NO POACHING.

## Confirmed baseline

The active model is the square–hexagon Hamiltonian

\[
\alpha=2H
=2\lambda+\lambda^2(-1+\cos4\phi)
+\lambda^3(1+\cos6\phi),
\]

with

\[
\rho=(2H)_p=2H_p,
\qquad
\omega=\frac{dq}{H_p}=\frac{2\,dq}{\rho}.
\]

The exact order-four certificate remains

\[
A_4\omega=d\left(\frac{V}{\rho^7}\right).
\]

Its Cartesian replay still passes exactly.  The sharp support transition remains
q-bound 25: failure, q-bound 27: closure.

## New inductive results

A finite-sum Lagrange-inversion generator now produces 400 exact coefficients
of

\[
\frac{T(\alpha)}{2\pi}
=\sum_{n\ge0}b(n)(\alpha/8)^n
\]

in a few seconds.  The operator ladder is:

| order | maximum coefficient degree | exact equations checked |
|---:|---:|---:|
| 4 | 14 | 396 |
| 5 | 10 | 395 |
| 6 | 8 | 394 |
| 8 | 7 | 392 |
| 12 | 6 | 388 |

Every residual is exactly zero on all available coefficient equations.

The leading coefficient of the order-4 operator factors as

\[
8\alpha(27\alpha^2+16)
(486\alpha^3-792\alpha^2+632\alpha-197)\,S_8(\alpha),
\]

where the degree-eight factor \(S_8\) is apparent.  At order 8 and order 12,
the leading coefficient is reduced to the geometric factor

\[
\Delta(\alpha)=
\alpha(27\alpha^2+16)
(486\alpha^3-792\alpha^2+632\alpha-197).
\]

Thus order 8 already removes all eight apparent leading singularities.  Order
12 does not reduce the leading degree further, but gives every operator
coefficient degree at most six.

## New deductive results

Exact Ore composition, performed over \(\mathbb Q(\alpha)\langle
\partial_\alpha\rangle\), verifies

\[
A_5=B_1A_4,
\qquad
A_6=B_2A_4,
\qquad
A_8=B_4A_4,
\qquad
A_{12}=B_8A_4.
\]

All four remainders are exactly zero.  Therefore the higher-order equations are
not independent guesses: they are rational left multiples of the already
certified order-four operator.  The differential certificate transfers
immediately:

\[
A_r\omega
=B_{r-4}(A_4\omega)
=d\bigl(B_{r-4}\Xi_4\bigr),
\]

with the usual interpretation that the parameter differential operator commutes
with the fiber differential.

## Bounded degree-optimality result

Using the 400 exact coefficients, the complete degree-\(\le5\) guessing matrix
has full column rank modulo the good prime 1000003 for every identifiable order
\(1\le r\le56\).  Hence, over \(\mathbb Q\), there is no nonzero polynomial-
coefficient annihilator of coefficient degree at most five anywhere in that
entire finite search range.

This is a rigorous bounded exclusion, not a proof for arbitrary order.  Within
the identifiable range, degree six is optimal, and the order-12/degree-6
operator reaches it.

## What this says inductively and deductively

Inductively, the exact data reveal an order–degree desingularization ladder

\[
(4,14)\to(5,10)\to(6,8)\to(8,7)\to(12,6).
\]

Deductively, exact Ore division proves that every displayed rung is generated
from the certified order-four equation.  Therefore future operator searches
should be used to optimize presentation—degree, apparent singularities, and
certificate size—not to rediscover the period relation.

## Next calculations

1. **Transfer the certificate explicitly to \(A_8\).**  This is the most
   geometrically natural operator because its leading polynomial is exactly
   \(\Delta(\alpha)\).  Compute and simplify the induced primitive
   \(\Xi_8=B_4\Xi_4\), then compare its pole order and support with the original
   \(V/\rho^7\).
2. **Compare \(A_8\) and \(A_{12}\) as human certificate presentations.**
   Order 8 minimizes apparent singularities; order 12 minimizes coefficient
   degree within the tested range.  Size both artifacts before choosing the
   publication-facing equation.
3. **Search for a direct primitive for \(A_8\), rather than mechanically
   applying \(B_4\).**  A direct exact-image backsolve may be much smaller than
   the transferred primitive.
4. **Use the q-support filtration deductively.**  Explain why the order-four
   primitive first closes at q-bound 27, and predict the closure bounds for the
   direct order-8 and order-12 backsolves.
5. **Only after that, vary the square–hexagon parameters.**  The fixed model now
   supplies a strong regression suite: 400 period terms, five annihilators,
   four Ore relations, and one exact Cartesian certificate.

## Replay

```text
python3 exact/verify_merged_certificate.py
python3 exact/verify_operator_ladder_400.py
python3 exact/verify_ore_relations.py
```

Expected final markers:

```text
MERGED_CERTIFICATE_PASS
OPERATOR_LADDER_400_PASS
ORE_RELATIONS_PASS
```
