# Square-hexagon certificate: deductive and reductive closure

Date: 2026-08-02  
Research owner: Bradley Klee  
Status: unpublished research; NO POACHING.

## 1. Model and period form

The active plane model is

\[
\alpha=2H(p,q)
=p^2+q^2-2p^2q^2+\frac14p^2(p^2-3q^2)^2.
\]

Set

\[
\rho=(2H)_p
=\frac p2\left(3p^4-12p^2q^2+9q^4-8q^2+4\right),
\qquad
\omega=\frac{dq}{H_p}=\frac{2\,dq}{\rho}.
\]

The closed certificate is

\[
\boxed{A_4\omega=d\left(\frac{V}{\rho^7}\right)}.
\]

Here \(A_4=\sum_{j=0}^4P_j(\alpha)\partial_\alpha^j\), with the exact
primitive integer polynomials stored in `exact/order4_operator.json`.
The full numerator \(V\) is stored in `exact/order4_xi.json`.

## 2. What is now deductive

The earlier route guessed \(A_4\) from the period series and then solved for
\(V\).  The new route starts from the Hamiltonian only.

For order \(r\), put all derivative forms

\[
\omega,\partial_\alpha\omega,\ldots,\partial_\alpha^r\omega
\]

over the common denominator \(\rho^{2r+1}\), and use primitives
\(V/\rho^{2r-1}\).  Symmetry reduces the numerator sector to even powers of
\(p\) and odd powers of \(q\), with reduced \(p\)-degree \(0,2,4\).

Let \(n=\deg_p+\deg_q\) be the source weight.  For the three source
monomials

\[
q^n,\qquad p^2q^{n-2},\qquad p^4q^{n-4},
\]

a top-symbol minor of the exact-image map is

\[
D_r(n)=419904\,
 (n-(8r-3))(n-(8r-4))(n-(6r-3)).
\]

Therefore \(D_r(n)\ne0\) for every \(n>8r-3\).  Starting with the highest
source weight and descending proves that the exact-image search is exhaustive
once

\[
p+q\le 8r-3.
\]

This replaces a guessed rectangular cutoff by a finite stopping theorem.

The exact quotient ranks are:

| order \(r\) | exhaustive weight | rows | exact columns | \(\operatorname{rank}C_r\) | \(\operatorname{rank}[C_r\mid W_r]\) | relation dimension |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5  | 17 | 6  | 6  | 8  | 0 |
| 2 | 13 | 29 | 18 | 18 | 21 | 0 |
| 3 | 21 | 41 | 30 | 30 | 34 | 0 |
| 4 | 29 | 53 | 42 | 42 | 46 | 1 |

Consequently:

1. no exact-differential relation occurs at orders 1, 2, or 3;
2. the order-4 relation space is one-dimensional;
3. fraction-free quotient reduction derives that relation without loading an
   operator;
4. clearing its denominator reproduces the stored \(P_0,\ldots,P_4\)
   coefficient for coefficient, with no scalar discrepancy;
5. the same backsolve reproduces the stored numerator \(V\) exactly.

Thus \(A_4\) is not merely series-guessed and subsequently certified.  It is
now independently derived as the first relation in the finite exact
cohomology reduction.

## 3. What is now reductive

The numerator has the symmetry-compressed form

\[
V=q\bigl(U_0(\alpha,q^2)+p^2U_1(\alpha,q^2)
                 +p^4U_2(\alpha,q^2)\bigr).
\]

It contains 40 nonzero coefficient polynomials and 514 expanded
\((\alpha,p,q)\)-terms.  Its maximum source weight is exactly 29, the
order-4 stopping weight.  The exact-image matrix has full column rank in this
sector, so the numerator is unique there.

There are no removable common factors:

- the gcd of the five operator polynomials is 1;
- the gcd of the 40 numerator coefficient polynomials in \(\alpha\) is 1;
- the numerical content of \(V\) is \(1/2\), so the all-integer form is
  \[
  2A_4\omega=d\left(\frac{2V}{\rho^7}\right).
  \]

Most importantly, the pole is reduced.  A lower pole would require
\(V\equiv\rho U\pmod{2H-\alpha}\).  Equivalently, \(V\) would vanish modulo
the ideal

\[
\langle 2H-\alpha,\rho\rangle.
\]

Exact Groebner reduction over \(\mathbb Q(\alpha)[p,q]\) gives a nonzero
normal form.  It factors as

\[
\operatorname{NF}(V)
=\frac{15q\,S_8(\alpha)}{2\alpha-1}
  R(\alpha,q^2),
\qquad R\ne0,
\]

where \(S_8\) is the degree-eight apparent factor in the leading coefficient
of \(A_4\).  Hence \(V\) is not divisible by \(\rho\) in the curve coordinate
ring, and \(\rho^7\) cannot be replaced by \(\rho^6\), or by any lower power.
The full normal form and its SHA-256 witness are in
`closure/closure_witness.json`.

The appearance of \(S_8\) in this ramification-divisor remainder is a useful
structural clue, but it is not yet claimed as a complete explanation of the
apparent singularities.

## 4. Exact closed statement

Let

\[
P_4=8\alpha(27\alpha^2+16)
(486\alpha^3-792\alpha^2+632\alpha-197)S_8(\alpha),
\]

with all \(P_j\) as stored in `exact/order4_operator.json`.  Let \(V\) be the
40-block numerator stored in `exact/order4_xi.json`.  Then the sparse
polynomial identity obtained after putting both sides over \(\rho^9\) and
reducing modulo \(2H-\alpha\) is identically zero:

\[
A_4\omega-d(V/\rho^7)=0.
\]

This statement has four independent replay layers:

1. direct sparse identity verification;
2. deductive derivation of \(A_4\) and \(V\) from quotient reduction;
3. exact order-minimality inside the exhaustive cohomology reduction;
4. reduced-pole verification by ideal membership.

## 5. What remains open

The certificate itself is mathematically closed under the stated conventions.
The following are presentation or extension problems, not gaps in the
identity:

- finding a clever change of energy variable that makes \(A_4\) prettier;
- explaining conceptually why the apparent factor \(S_8\) occurs;
- classifying the surrounding square-hexagon parameter stratum;
- proving any stronger statement about cycle-specific annihilators outside the
  exact cohomology relation considered here.

## 6. Replay

From the packet root, run:

```text
python3 exact/verify_merged_certificate.py
python3 exact/derive_deductive_certificate.py
python3 exact/verify_reduced_primitive.py
python3 exact/verify_operator_ladder_400.py
python3 exact/verify_ore_relations.py
```

Expected markers:

```text
MERGED_CERTIFICATE_PASS
DEDUCTIVE_CERTIFICATE_PASS
REDUCED_PRIMITIVE_PASS
OPERATOR_LADDER_400_PASS
ORE_RELATIONS_PASS
```
