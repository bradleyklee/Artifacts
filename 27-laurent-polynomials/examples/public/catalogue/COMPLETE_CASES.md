# Explicit Laurent examples and certificates

## Publication-safe count

There are four fully verified Laurent/isoperiodic examples among the 11 plane
Hamiltonians: models 1, 2, 3, and 9.

Every complete case has:

- an exact Hamiltonian telescoping certificate;
- an exact Laurent telescoping certificate;
- a common second-order ODE;
- the same normalized analytic germ.

The complete certificate files are copied into `02_verified_complete_cases/`.

---

## Model 1 — \(I_1,I_1,I_1,III^*\)

Hamiltonian:

\[
E=p^2+q^2+pq^2+q^3.
\]

Arithmetic scale:

\[
t=E/32.
\]

Sequence:

\[
1,36,5460,1053360,225765540,\ldots
\]

Laurent polynomial:

\[
P_1(w,x)=\frac{(1+w)^3}{w^2}G_1(x),
\]

where

\[
\begin{aligned}
G_1(x)={}&-ix^3+(2+4i)x^2+(-8-5i)x+12\\
&+(-8+5i)x^{-1}+(2-4i)x^{-2}+ix^{-3}.
\end{aligned}
\]

The Laurent coefficients lie in \(\mathbb Z[i]\); the constant terms are
rational and hence ordinary integers.

---

## Model 2 — \(I_1,I_1,I_2,IV^*\), OEIS A303790

Hamiltonian:

\[
E=p^2+q^2+p^3+q^3.
\]

Arithmetic scale:

\[
t=E/32.
\]

Sequence:

\[
1,60,7380,1090320,176978340,\ldots
\]

Laurent polynomial:

\[
\boxed{
P_2(w,y)=
\frac{(1+w)^3(1+y)^2(y^2-4y+1)^2}{w^2y^3}.
}
\]

Thus

\[
A_n=[P_2(w,y)^n]_0.
\]

The complete note, scalar period certificate, graph code, and Laurent
certificate are bundled under `04_figures_and_note_example/`.

---

## Model 3 — \(I_1,I_1,II,IV^*\)

Hamiltonian:

\[
E=p^2+q^2-p^3-3p^2q-2q^3.
\]

Arithmetic scale:

\[
t=E/32.
\]

Sequence:

\[
1,276,162900,114036720,86213649060,\ldots
\]

Laurent polynomial:

\[
P_3(w,x)=\frac{(1+w)^3}{w^2}G_3(x),
\]

where

\[
\begin{aligned}
G_3(x)={}&-ix^3+(-6-12i)x^2+(-24-21i)x+92\\
&+(-24+21i)x^{-1}+(-6+12i)x^{-2}+ix^{-3}.
\end{aligned}
\]

Again the polynomial is over \(\mathbb Z[i]\), while its constant terms are
ordinary integers.

---

## Model 9 — \(I_1,I_1^*,I_2,I_2\)

Hamiltonian:

\[
E=p^2+q^2+(q^2-4p^2)^2.
\]

Arithmetic scale:

\[
t=E/16.
\]

Sequence:

\[
1,-172,95076,-67123120,52467923620,\ldots
\]

Laurent polynomial:

\[
P_9(w,x)=
\frac{(1+w)^2}{w}
\left(
-25x^2-60x-86-60x^{-1}-25x^{-2}
\right).
\]

---

## Remaining seven examples

All seven remaining models have:

- an explicit Hamiltonian;
- 31 exact period coefficients;
- a recurrence;
- a second-order ODE;
- a proved safe all-\(n\) integral scaling.

They do not yet have publication-safe Laurent identifications with both exact
certificates. Their complete data are in

`03_all_11_period_examples/plane_period_round_11_v1/round_data.json`.

---

## Quarantine warning

The directory `90_quarantine_candidates/failed_expansion_v2/` contains
candidate Laurent formulas for models 5 and 7. A reconstruction run failed an
exact scalar Hamiltonian-certificate assertion. These formulas are leads only
and must not be cited as completed examples.
