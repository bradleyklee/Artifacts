# Mixed cubic--quartic algorithm data report

## Purpose

This corpus is intended as algorithm training and regression data, not as a
collection of exceptional hand-picked examples. Every model has both cubic and
quartic terms. The corpus contains dense generic mixtures, semi-dense mixtures,
aligned and chiral angular controls, cubic-plus-radial models, rotated
one-coordinate mechanical models, and separable/near-separable controls.

For each model the following modes were exercised:

1. **Inductive:** 270 period coefficients modulo each of two primes, followed by
   an ODE search through order 6 and coefficient degree 35.
2. **Reductive:** reduction of the differential integrands
   `omega, d_alpha omega, ...` modulo exact differentials, with quotient ranks
   computed at two independent prime/alpha pairs.
3. **Deductive:** when the homogeneous quartic layer is squarefree, the finite
   source bound `B_r = 6r - 3` was applied at every order through the first
   relation.
4. **Exact characteristic zero:** the three order-two mixed models were solved
   over `Q(alpha)` and their exact differential identities verified.
5. **Integer series:** exact rational period coefficients were computed for the
   order-two models and integerized by a geometric energy rescaling.

## Corpus balance

- Total models: **43**.
- Dense generic, all four cubic and all five quartic monomials: **20**.
- Semi-dense generic: **6**.
- Structured controls: **17**.
- Models with no nontrivial signed-coordinate symmetry: **39**.
- Generic/semi-generic models with no such symmetry: **26**.

The corpus is therefore dominated by ordinary mixed models rather than odd
special examples.

## Pipeline statistics

All **43/43** models passed at both primes.

- Inductive/reductive first-order agreement: **43/43**.
- First relation order 2: **3** models.
- First relation order 4: **3** models.
- First relation order 6: **37** models.

Order--degree distribution:

| First box | Count |
|---|---:|
| `(2,4)` | 3 |
| `(4,13)` | 1 |
| `(4,14)` | 2 |
| `(6,20)` | 3 |
| `(6,29)` | 3 |
| `(6,31)` | 31 |

The 20 fully dense generic models all landed at exactly `(order,degree)=(6,31)`.
The six semi-dense generic models did the same.

## Deductive bound coverage

For **37/43** models the quartic layer was squarefree at infinity. The generic
bound

```text
B_r = 6*r - 3
```

was used to make each reduced-integrand rank calculation finite. At order six
this means 130 exact-image source columns and, in the dense cases, 146 nonzero
ambient rows. Orders one through five had relation dimension zero; order six
had relation dimension one.

Six models had degenerate quartic layers:

- three dense-cubic plus radial-quartic models;
- three rotated one-coordinate mechanical models.

Their reductions were still run with conservative empirical bounds, but those
six lower-order exclusions are not claimed as consequences of the generic
squarefree bound.

## What the mixed search says about order two

In this corpus, order two occurred only for

```text
E = p^2 + q^2 + a*L(p,q)^3 + b*L(p,q)^4,
```

where the cubic and quartic depend on the same linear coordinate `L`. The three
rationally rotated versions all produced order 2, degree 4.

Thus the data do not support treating order two as common among arbitrary
cubic--quartic mixtures. It is a special low-rank locus, but it is stable under
canonical rotation and is an excellent regression family.

## Exact order-two differential reductions

All three rotated mechanical models satisfy an exact identity

```text
A_2(omega) = d(V/rho^3).
```

For each model:

- exact-image columns: 28;
- ambient rows: 46;
- primitive coefficient blocks: 21;
- expanded primitive terms: 70;
- operator coefficient degrees: 2, 3, 4;
- exact polynomial identity: PASS.

These examples use all four cubic monomials and all five quartic monomials after
rotation, despite belonging to a one-coordinate family.

## Hidden-reflection diagnostic

For the eight harmonic controls, let `A3` and `A4` be the complex amplitudes of
the angular frequencies 3 and 4. A common reflection axis is detected by

```text
imag(A3^4 * conjugate(A4)^3) = 0.
```

Exactly three controls satisfied this condition, and exactly those three
closed at order four. The other five closed at order six. This condition was
more informative than coordinate-axis symmetry, because one order-four case
had only a hidden rotated reflection.

## Other useful strata

- Dense generic mixtures: order 6, degree 31.
- Cubic plus radial quartic: order 6, degree 20.
- Separable cubic--quartic sums: order 6, degree 29.
- Near-separable perturbation: order 6, degree 31.
- Common-reflection 3+4 harmonic mixtures: order 4, degree 13 or 14.

These strata provide distinct regression targets for coefficient degree and
matrix size even when the differential order is unchanged.

## Integerized period data

For `T(alpha)/(2*pi) = sum c_n alpha^n`, the three exact order-two models give:

```text
mechanical_rotated_01, K=5600:
1, -180, -916860, 2874619440, -1413074442780, ...

mechanical_rotated_02, K=2240:
1, 660, 1905540, 7098223440, 29374181256420, ...

mechanical_rotated_03, K=11200:
1, 4260, 50178660, 730878289680, 11702704129536420, ...
```

Here the integer sequence is `K^n c_n`. Twenty-four exact terms were generated
for each model and checked against both modular series term-for-term.

Exact quoted-prefix searches found no indexed OEIS or official OEIS-export
match. Direct OEIS API confirmation was unavailable in this run, so these are
recorded as candidate no-matches, not definitive new OEIS sequences.

## Practical conclusion

The present data factory is exercising all three mathematical modes:

```text
period series -> candidate ODE
reduced differential integrands -> quotient relation
finite top-symbol bound -> exhaustive lower-order search
```

For ordinary squarefree mixed quartics, the stable baseline is order 6,
degree 31. Low-order models should now be found by solving rank-drop conditions
inside controlled coefficient families, while the generic models remain
valuable for regression and performance statistics.
