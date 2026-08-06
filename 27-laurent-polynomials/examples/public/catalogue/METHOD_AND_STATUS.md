# Eleven-model plane period and Laurent constant-term round

## Result at a glance

All eleven positive plane Hamiltonians were processed with the fixed local
normalization

\[
E=2H,\qquad E(0,0)=0,\qquad \operatorname{Hess}(2H)(0,0)=2I.
\]

For every model I computed 31 exact coefficients of

\[
\Pi(E)=\frac{T(E)}{2\pi}=\sum_{n\geq0}a_nE^n.
\]

When a finite real singular level bounds the oscillation disk, the geometric
base coordinate is

\[
x=\frac{E}{E_b},
\]

so the bounding separatrix is at \(x=1\).  The arithmetic coordinate is kept
separate:

\[
t=\frac{E}{M}.
\]

This distinction is necessary: the best geometric scale and the best
integrality scale usually differ.

## What closed completely

Four models now have the full chain:

\[
\boxed{
\text{Hamiltonian period}
\longleftrightarrow
[F^n]_0
\longleftrightarrow
\text{same exact annihilator}.
}
\]

They are

\[
\begin{aligned}
&I_1,I_1,I_1,III^*,\\
&I_1,I_1,I_2,IV^*,\\
&I_1,I_1,II,IV^*,\\
&I_1,I_1^*,I_2,I_2.
\end{aligned}
\]

For each of these:

1. the Hamiltonian side has an exact divergence certificate
   \[
   L_E\!\left(\frac1{2H-E}\right)
   =
   \partial_p\!\left(\frac{P}{(2H-E)^2}\right)
   +
   \partial_q\!\left(\frac{Q}{(2H-E)^2}\right);
   \]
2. the Laurent side has an exact telescoping certificate for the
   constant-term recurrence;
3. both residuals expand to zero;
4. the common analytic solution is fixed by \(\Pi(0)=1\);
5. integrality follows from the integral Laurent model.

Two Laurent polynomials have coefficients in \(\mathbf Z\).  The two
reflection-asymmetric cubic cases currently use \(\mathbf Z[i]\).  Their
constant terms are rational, hence lie in

\[
\mathbf Z[i]\cap\mathbf Q=\mathbf Z.
\]

A real \(\mathbf Z\)-Laurent presentation for those two remains open.

## Exact period formulas

For a pure cubic perturbation

\[
E=r^2+r^3g_3(\theta),
\]

Lagrange inversion gives

\[
a_n=\binom{3n}{2n}\left\langle g_3^{2n}\right\rangle .
\]

This immediately produces the Laurent model

\[
F(w,z)=\frac{(1+w)^3}{w^2}\,M g_3(z)^2.
\]

For the structured quartic class

\[
E=r^2+r^3g_3(\theta)+r^4g_4(\theta),
\qquad
g_3=L_2L_1,\quad g_4=\mu L_2^2,
\]

the exact coefficient formula is

\[
a_n=
\sum_{m=0}^n
(-\mu)^{n-m}
\frac{(2n+m)!}{n!(2m)!(n-m)!}
\left\langle L_2^{2n}L_1^{2m}\right\rangle .
\]

This formula generated all quartic series without numerical integration.

## Integrality for all eleven

Every model has a proved all-\(n\) integral rescaling, although the safe scale
is not always the smallest one observed in the first 31 terms.

The proof uses

\[
4^{A+B}\left\langle p^{2A}q^{2B}\right\rangle
=
\frac{(2A)!(2B)!}{A!B!(A+B)!},
\]

the integral super-Catalan number, together with the integral multinomial
factor

\[
\frac{(2n+m)!}{n!(2m)!(n-m)!}.
\]

For the structured quartic parameters

\[
L_2=q^2-rp^2,\qquad L_1=\sqrt U\,p+\sqrt V\,q,
\]

a sufficient scale is

\[
M_{\rm safe}
=
64\,\operatorname{den}(r)^2
\operatorname{den}(U)
\operatorname{den}(V)
\operatorname{den}(\mu).
\]

This is deliberately conservative.  The much smaller scales in
`STATUS_TABLE.md` made all first 31 coefficients integral, but remain to be
proved for the seven cases without Laurent models.

## Current boundary

- **11/11:** exact period coefficients and exact candidate ODEs;
- **11/11:** all-\(n\) integrality at a proved scale;
- **4/11:** explicit Laurent \(F\);
- **4/11:** exact annihilator derived independently on both sides;
- **7/11:** smaller arithmetic scale and Laurent realization still open.

The first completed pilot is therefore not isolated: four models now satisfy
the requested double-certificate standard.
