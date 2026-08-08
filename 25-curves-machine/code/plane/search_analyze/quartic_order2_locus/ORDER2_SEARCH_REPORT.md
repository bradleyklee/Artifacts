# Order-two quartic search report

## Purpose

Narrow the quartic search to the simplest Picard--Fuchs cases and identify
coefficient families that can be solved or specialized after the differential
relation is derived.

All modular first-hit statements below agree at primes 65521 and 65497.
The exact certificates use

\[
E=2H,\qquad \rho=E_p,\qquad \omega=\frac{2\,dq}{\rho},
\]

and derive a relation among \(\omega,\partial_\alpha\omega,
\partial_\alpha^2\omega\) modulo exact differentials.

## Search totals

Among 28 controlled models:

- 1 first closed at order 1;
- 19 first closed at order 2;
- 7 first closed at order 4;
- 1 had no relation through the tested order-6/degree-35 box.

## Clean exact certificate A: factored cubic

\[
E=p^2+q^2+\frac{(p+q)(p-q)^2}{5}.
\]

The exact period equation is

\[
(16\alpha^2-50\alpha)T''+(32\alpha-50)T'+3T=0.
\]

Reductive certificate data:

```text
rows                 30
exact-image columns  18
combined rank        20
relation dimension    1
primitive blocks     15
expanded terms       18
primitive pole       rho^3
```

## Clean exact certificate B: even quartic

\[
E=p^2+q^2+\frac{p^4+p^2q^2}{4}.
\]

The exact period equation is

\[
(4\alpha^2+4\alpha)T''+(8\alpha+4)T'+T=0.
\]

Reductive certificate data:

```text
rows                 22
exact-image columns  12
combined rank        14
relation dimension    1
primitive blocks      6
expanded terms        9
primitive pole       rho^3
```

## Additional exact certificates

### Mechanical cubic-plus-quartic

\[
E=p^2+q^2+\frac{q^3}{5}+\frac{q^4}{7}.
\]

It closes exactly at order two with 19 ambient rows, 14 source columns,
7 nonzero primitive blocks, and 21 expanded primitive terms.  Its operator is
less attractive only because the arbitrary coefficients 1/5 and 1/7 inflate
the integer normalization.

### Generic cubic with all cubic monomials

\[
E=p^2+q^2+\frac{p^3}{7}+\frac{p^2q}{9}
-\frac{pq^2}{11}+\frac{q^3}{13}.
\]

This has no nontrivial signed-coordinate symmetry, yet the exact differential
reduction still closes at order two.  The certificate uses 30 rows, 18 source
columns, 17 primitive blocks, and 82 expanded terms.  The operator coefficients
are large, showing why posterior coefficient specialization is useful.

## Supported order-two loci

The experiments support four useful families.

1. **Cubic-only:** \(E=Q_2+C_3\).  A generic plane cubic is already a
genus-one problem, and two unrelated all-coefficient tests close at order two.

2. **Even quartic:** \(E=Q_2+Q_4\).  Central inversion survives even when no
coordinate reflection survives.  Two generic five-coefficient quartics close
at order two, degree seven.

3. **Mechanical quartic:** after a linear canonical rotation,
\(E=P^2+V(Q)\), with \(\deg V\le4\).  Mixed cubic and quartic terms remain
order two when they depend on the same coordinate.

4. **Single angular cubic frequency plus radial quartic:** frequencies 1 and 3,
including arbitrary rotated phase, both close at order two.

The purely radial quartic closes at order one.

## Boundaries found

- Mixing the two independent cubic frequencies and adding a radial quartic
  raises the first relation to order four.
- Mixing cubic and nonradial quartic frequencies generally raises the order to
  four; phase-mismatched triangle-square mixtures previously rose to order six.
- A sum of unrelated nonlinear functions of both canonical coordinates is not
  automatically order two.

## Posterior coefficient strategy

The next symbolic search should work inside one order-two family at a time.
Introduce variable amplitudes, derive the order-two relation up to scale, and
then solve the amplitudes for secondary objectives:

- small integer operator coefficients;
- low coefficient degree;
- factorized leading coefficient;
- prescribed reflection or hidden rotation symmetry;
- short exact primitive;
- integral or nearly integral period series.

The first recommended variable families are

\[
E=p^2+q^2+a p^3+b p^2q+c pq^2+d q^3
\]

and

\[
E=p^2+q^2+a p^4+b p^3q+c p^2q^2+d pq^3+e q^4.
\]

Both are generically order two within their respective degree strata.  They are
therefore better coefficient laboratories than mixed cubic-plus-quartic models,
where order four or six is generic.
