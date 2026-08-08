# Semi-random quartic certificate search — 2026-08-02

## Conventions

For every model,

\[
E=2H,\qquad \rho=E_p=2H_p,\qquad
\omega=\frac{2\,dq}{\rho}=\frac{dq}{H_p}.
\]

The inductive stage computes the small-period series and searches for
polynomial-coefficient ODEs.  The reductive stage forms the derivative columns
\(W=[\omega,\partial_\alpha\omega,\ldots]\), the exact-image matrix \(C\),
and searches for relations in the quotient by `im(C)`.

## Correction to the first Q1 run

The first screen started at order 6 and found an exact `(order, degree)` pair
`(6,8)`.  A later downward scan found the actual first relation at `(4,14)`.
The observed ladder is

```text
(4,14) -> (5,10) -> (6,8) -> (8,7).
```

Thus the order-6 equation is a lower-degree higher-order presentation, not the
minimal operator.  The exact order-4 operator was reconstructed and verified
against 160 exact coefficients.  Its primitive integer coefficients reach 59
digits.

## Sweep of p-even cubic-plus-quartic models

Five small-coefficient models retaining only `p -> -p` were screened.  Four
of them (`q1b`, `q1c`, `q1d`, `q1f`) show the same first operator box and
tradeoff ladder as Q1:

```text
first: (4,14)
later: (5,10), (6,8), (8,7)
```

The radial-quartic model `q1e` is cleaner:

```text
first: (4,11)
later modular boxes: (5,8), (7,6), (10,5)
```

This repeated order-four behavior is consistent with the rank-four symmetry
subsystem selected by `p -> -p`.

## Exact certificate Q1e — exhaustive

Model:

\[
E=p^2+q^2+\frac{(p^2+q^2)^2}{4}
  +\frac{p^2q+2q^3}{5}.
\]

Within signed coordinate permutations, only the identity and `p -> -p`
survive.

The top symbol of the exact-image map has determinant

\[
S_r(n)=\frac{8}{25}(n-(5r-2))(2n-(10r-5)).
\]

Therefore source weight `5r-2` is exhaustive.  Exact ranks are:

| order | stopping weight | rows | exact columns | rank C | rank [C|W] | relations |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | 14 | 6 | 6 | 8 | 0 |
| 2 | 8 | 24 | 16 | 16 | 19 | 0 |
| 3 | 13 | 34 | 26 | 26 | 30 | 0 |
| 4 | 18 | 44 | 36 | 36 | 40 | 1 |

The unique null relation gives the exact order-four, degree-eleven operator and
simultaneously reconstructs the primitive:

\[
A_4\omega=d\!\left(\frac{V}{\rho^7}\right).
\]

Data:

```text
operator coefficient degrees: 7, 8, 9, 10, 11
maximum primitive-integer coefficient size: 30 digits
primitive coefficient blocks: 36
expanded primitive terms: 349
maximum source weight: 18
```

The reductively derived operator equals the independently series-derived
operator exactly, with scalar ratio 1.

## Exact certificate Q1b — exact identity, partial minimality proof

Model:

\[
E=p^2+q^2+\frac{p^4+p^2q^2+2q^4}{4}
  +\frac{p^2q+q^3}{3}.
\]

Again, only the identity and `p -> -p` survive among signed coordinate
permutations.

The exact order-four, degree-fourteen operator was reconstructed from 160 exact
period coefficients.  The reductive matrix at source weight 21 has

```text
rows: 50
exact columns: 42
rank C: 42
rank [C|W]: 46
relation dimension: 1
```

Using the exact operator, the unique exact backsolve gives

\[
A_4\omega=d\!\left(\frac{V}{\rho^7}\right)
\]

and the sparse identity verifies exactly.

```text
primitive coefficient blocks: 42
expanded primitive terms: 523
maximum source weight: 21
maximum operator coefficient size: 36 digits
```

Orders 1 through 3 have no modular derivative relation through source weight
28 at two generic finite-field evaluations.  A complete characteristic-zero
stopping theorem for this nonradial case has not yet been written, so the exact
certificate is closed while the strict minimal-order proof remains partly
modular/inductive.

## Fully asymmetric quartic Q2 — modular rank-six result

Model:

\[
\begin{aligned}
E={}&p^2+q^2+
\frac{3p^4+2p^3q-4p^2q^2+pq^3+5q^4}{12}\\
&+\frac{p^3-2p^2q+pq^2+3q^3}{15}.
\end{aligned}
\]

No nontrivial signed coordinate symmetry survives.

Finite-field Fourier series generated 340 coefficients at each of two primes.
The first operator box is

```text
order 6, degree 31
unknowns: 224
training equations: 254
held-out equations: 80 per prime
```

Both primes pass every held-out equation.  No relation was found through order
5 in every identifiable box.  The reductive screen using all four p-residue
sectors first closes at

```text
order: 6
rectangular primitive q-bound: 32
ambient rows: 158
exact columns: 132
rank C: 132
rank [C|W]: 138
relation dimension: 1
```

This agrees at three generic finite-field evaluations.  The exact rational
operator and primitive have not yet been reconstructed.

## Main structural result of the sweep

The experiments distinguish symmetry rank from polynomial degree:

```text
quartic with p-reflection only  -> first period operator order 4
quartic with no reflection     -> first period operator order 6
```

The order-four ladder seen in the square-hexagon example is not isolated; it
reappears across generic p-even quartics.  Removing the involution restores the
full rank-six genus-three period system.

## Next implementation targets

1. Generalize the top-symbol/stopping calculation from Q1e to arbitrary
   p-even quartics.
2. Reconstruct the asymmetric Q2 order-six operator by modular CRT.
3. Implement modular reductive nullspaces and interpolation over `Q(alpha)` so
   the 158-by-139 Q2 calculation does not require a monolithic symbolic solve.
4. Factor higher-order operator ladders by exact Ore division once the minimal
   operators are reconstructed.
