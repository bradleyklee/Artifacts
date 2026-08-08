# Universal order-two equation for the homogeneous cubic perturbation

## Family and notation

Let

\[
H(p,q)=p^2+q^2+a p^3+b p^2q+c pq^2+dq^3,
\qquad H(p,q)=\alpha,
\]

and let

\[
T(\alpha)=\oint \frac{2\,dq}{H_p}.
\]

The derivative in the denominator is the function \(H_p\). No notation of the
form \(E_p\) is used.

Homogenize the level curve as the ternary cubic

\[
U(p,q,z)=a p^3+b p^2q+c pq^2+dq^3+(p^2+q^2)z-\alpha z^3.
\]

## Ternary-cubic invariants

For this sparse cubic, Fisher's normalized invariants reduce to

\[
\begin{aligned}
c_4={}&-16\bigl(9a\alpha c-3\alpha b^2+9\alpha bd
                  -3\alpha c^2-1\bigr),\\
c_6={}&8\bigl(8+\alpha L+\alpha^2M\bigr),
\end{aligned}
\]

where

\[
L=-108a^2+108ac-72b^2+108bd-72c^2-108d^2,
\]

and

\[
M=729a^2d^2-486abcd+108ac^3+108b^3d-27b^2c^2.
\]

Thus \(c_4\) is linear and \(c_6\) is quadratic in \(\alpha\).

Define

\[
\Delta=c_4^3-c_6^2,
\qquad
G=2c_4c_6'-3c_6c_4',
\]

where primes mean \(d/d\alpha\).

## Universal equation

Every period \(T\) satisfies

\[
P_2T''+P_1T'+P_0T=0,
\]

with

\[
\begin{aligned}
P_2={}&144\Delta G,\\
P_1={}&144(\Delta'G-\Delta G'),\\
P_0={}&12(\Delta''G-\Delta'G')
       -9Gc_4(c_4')^2+4G(c_6')^2.
\end{aligned}
\]

After dividing the three coefficients by their common polynomial and integer
content, their generic degrees in \(\alpha\) are

\[
(\deg P_0,\deg P_1,\deg P_2)=(4,5,6).
\]

The expanded coefficient data are included in
`data/general_cubic_order2_coefficients_by_alpha.json`. The compact invariant
form is preferable for human use; the expanded form contains 426, 441, and 445
multivariate terms before collecting by powers of \(\alpha\).

## Is the minimal order always two?

For a smooth projective cubic fiber, the period system has rank two, so the
period is annihilated by an operator of order at most two. For a non-isotrivial
generic family, the minimal order is two. It can drop on special loci:

- the cubic part may vanish or the family may cease to be a genuine smooth
  cubic family;
- \(\Delta\) may vanish identically, giving singular fibers rather than an
  elliptic family;
- \(G\) may vanish identically, so the displayed cyclic-vector operator
  degenerates and a lower-order/isotrivial treatment is required;
- specialization can introduce common factors and lower the energy degrees
  without lowering the differential order.

Hence: **order at most two for smooth cubic periods; generically and in the
fully asymmetric case, exactly two.**

## Independent checks

1. The formula specializes exactly, up to one common scalar, to all three
   archived characteristic-zero cubic operators available in the transfer:
   `generic_cubic_all_A`, `cubic_three_lines`, and `simple_cubic_factor`.
2. For the independent fully asymmetric model `generic_cubic_all_B`, the
   specialization annihilates all 172 checkable coefficients of each modular
   period series at primes 65497 and 65521.
3. The fully asymmetric `generic_cubic_all_A` specialization matches the
   archived operator in all three derivative blocks, not merely in degree or
   leading factor.

## Files

- `src/derive_cubic_invariants_from_hessian.py`: derives \(c_4,c_6\) from the
  Hessian-pencil identity.
- `src/derive_general_cubic_operator.py`: constructs and expands the universal
  operator.
- `src/verify_exact_specializations.py`: checks exact archived operators.
- `src/verify_modular_series.py`: checks the independent modular period data.
- `data/general_cubic_order2_operator.json`: compact and expanded operator.
- `data/general_cubic_order2_coefficients_by_alpha.json`: coefficients collected
  by powers of \(\alpha\).
