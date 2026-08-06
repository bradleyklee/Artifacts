# Transfer packet: A303790 cubic period note

## Assignment

Write a short, self-contained note around the plane Hamiltonian

\[
E=K(p,q)=p^2+q^2+p^3+q^3.
\]

The note must accomplish three things:

1. give a clean code-generated picture of the two real period disks and the
   Abel--Wick traces;
2. prove that all closed periods satisfy one explicit second-order
   Picard--Fuchs equation;
3. derive the same equation independently from an integral Laurent polynomial
   and identify the normalized period coefficients with its constant terms.

Do not use image generation. Do not locate critical points numerically.
Everything needed for the geometry and the certificates is algebraic and is
included here.

---

## Recommended note structure

### 1. State the model and the two normalizations

Use

\[
K=p^2+q^2+p^3+q^3.
\]

The finite critical values are

\[
0,\qquad \frac4{27},\qquad \frac8{27}.
\]

Keep the two useful variables distinct:

\[
x=\frac{27E}{4},
\qquad
t=\frac{E}{32}=\frac{x}{216}.
\]

The variable \(x\) puts the bounding critical energy at \(x=1\).  The variable
\(t\) produces the integer series.

The fiber configuration is

\[
I_1,I_1,I_2,IV^*.
\]

### 2. Explain the two real period disks

Use the exact 45-degree rotation

\[
p=\frac{u+v}{\sqrt2},
\qquad
q=\frac{u-v}{\sqrt2}.
\]

Then

\[
K=u^2+v^2+\frac{u}{\sqrt2}(u^2+3v^2).
\]

At the critical energy,

\[
K-\frac4{27}
=
\frac{\sqrt2}{2}
\left(u+\frac{\sqrt2}{3}\right)
\left[
\left(u+\frac{\sqrt2}{3}\right)^2
+3v^2-\frac23
\right].
\]

Thus the critical level consists of a line and an ellipse.  The line segment
between the two saddle points divides the ellipse into two disks.

The critical points in rotated coordinates are

\[
\begin{array}{c|c}
(0,0)&E=0\quad\text{minimum}\\
(-\sqrt2/3,\pm\sqrt2/3)&E=4/27\quad\text{saddles}\\
(-2\sqrt2/3,0)&E=8/27\quad\text{maximum}.
\end{array}
\]

For the main picture plot:

- \(E=1/27,2/27,3/27\) in the disk surrounding the minimum;
- \(E=5/27,6/27,7/27\) in the disk surrounding the maximum;
- the ellipse and dividing line at \(E=4/27\) with heavier lines.

Use `figures/make_figures.py`.  It produces PNG, PDF, and SVG output.

### 3. Record the exact symmetry between the disks

The affine involution

\[
\iota(p,q)=\left(-p-\frac23,-q-\frac23\right)
\]

satisfies

\[
K(\iota(p,q))=\frac8{27}-K(p,q).
\]

Consequently, after choosing cycle orientations so both limiting periods are
positive, the two local period expansions use the same integer sequence:

\[
\Pi_0(E)
=
\sum_{n\ge0}A_n\left(\frac{E}{32}\right)^n,
\]

and

\[
\Pi_8(E)
=
\sum_{n\ge0}A_n
\left(\frac{8/27-E}{32}\right)^n.
\]

This is the clean way to discuss “multiple periods.”  The Laurent model below
proves the coefficients for both disks because the involution identifies the
two local problems exactly.

### 4. Abel--Wick continuation

Apply \(v\mapsto iy\).  Then

\[
K_{\mathrm W}
=
u^2-y^2+\frac{u}{\sqrt2}(u^2-3y^2).
\]

At \(E=4/27\),

\[
K_{\mathrm W}-\frac4{27}
=
\frac{\sqrt2}{2}
\left(u+\frac{\sqrt2}{3}\right)
\left[
\left(u+\frac{\sqrt2}{3}\right)^2
-3y^2-\frac23
\right].
\]

The figure script plots the energy families from the two disks separately.
Call these real traces of the complexified curves.  Do not claim that a single
real Wick slice by itself is a proof that the whole complex torus has been
displayed.

### 5. Prove the period ODE

Let

\[
\omega_E=\frac{2\,dq}{K_p}.
\]

The factor 2 is present because \(K=2H\).  At fixed \(q\), put

\[
D_E=\frac1{K_p}\partial_p.
\]

Use the operator

\[
\begin{aligned}
L_E={}&E(27E-8)(27E-4)D_E^2\\
&+(2187E^2-648E+32)D_E\\
&+15(27E-4).
\end{aligned}
\]

The scalar certificate supplied in `period_certificate/` has the form

\[
\Xi(E,p,q)=\frac{V(E,p,q)}{K_p^3}
\]

and verifies on \(K=E\)

\[
L_E(\omega_E)=d\Xi.
\]

In coefficient form,

\[
L_E\!\left(\frac2{K_p}\right)
=
\partial_q\Xi-\frac{K_q}{K_p}\partial_p\Xi.
\]

The verification script clears denominators and reduces the numerator modulo
\(K-E\); the remainder is exactly zero.

Therefore every closed period cycle satisfies

\[
\boxed{
E(27E-8)(27E-4)\Pi''
+(2187E^2-648E+32)\Pi'
+15(27E-4)\Pi=0.
}
\]

The certificate proves the equation simultaneously for the cycles in both
real disks and for their analytic continuations.

Put the full polynomial \(V\) in an appendix or supplementary data rather
than interrupting the main argument.

### 6. Derive the period coefficients directly

In polar coordinates for the rotated model,

\[
K=r^2+r^3g(\theta),
\qquad
g(\theta)=\frac{3\cos\theta-\cos3\theta}{2\sqrt2}.
\]

Let \(r(E,\theta)\) be the small radial solution and let

\[
\mathcal A(E)=\frac12\int_0^{2\pi}r(E,\theta)^2\,d\theta.
\]

Since \(K=2H\),

\[
\Pi(E)=\frac{T(E)}{2\pi}
=\frac1\pi\frac{d\mathcal A}{dE}.
\]

Lagrange inversion applied to

\[
E=r^2(1+rg)
\]

gives

\[
r^2
=
\sum_{n\ge0}
\frac1{n+1}\binom{3n}{2n}
g(\theta)^{2n}E^{n+1}.
\]

Hence

\[
\Pi(E)
=
\sum_{n\ge0}
\binom{3n}{2n}
\left\langle g^{2n}\right\rangle E^n,
\]

where the angle brackets denote angular average.

### 7. Convert the coefficients to a Laurent constant term

Put \(z=e^{i\theta}\) and define

\[
L(z)=3(z+z^{-1})-(z^3+z^{-3}).
\]

Then

\[
g^2=\frac{L(z)^2}{32}.
\]

Moreover,

\[
L(z)^2
=
\frac{(1+z^2)^2(z^4-4z^2+1)^2}{z^6}.
\]

Writing \(y=z^2\), define

\[
C(y)=
\frac{(1+y)^2(y^2-4y+1)^2}{y^3}.
\]

The binomial factor is also a constant term:

\[
\binom{3n}{2n}
=
\left[
\left(\frac{(1+w)^3}{w^2}\right)^n
\right]_0.
\]

Therefore define the integral Laurent polynomial

\[
\boxed{
\Phi(w,y)=
\frac{(1+w)^3(1+y)^2(y^2-4y+1)^2}{w^2y^3}.
}
\]

Then

\[
\boxed{A_n=[\Phi(w,y)^n]_0}
\]

and

\[
\Pi_0(E)
=
\sum_{n\ge0}A_n\left(\frac{E}{32}\right)^n.
\]

The first terms are

\[
1,\ 60,\ 7380,\ 1090320,\ 176978340,\ldots
\]

and agree with OEIS A303790.

Because \(\Phi\) has integer Laurent coefficients, this identity proves
\(A_n\in\mathbb Z\).

### 8. Derive the same ODE from the Laurent polynomial

Factor

\[
\Phi(w,y)=B(w)C(y),
\qquad
B(w)=\frac{(1+w)^3}{w^2}.
\]

Write

\[
b_n=[B^n]_0=\binom{3n}{2n},
\qquad
c_n=[C^n]_0,
\qquad
A_n=b_nc_n.
\]

The exact rational certificate `laurent/certificate_R.txt` verifies

\[
P_0(n)+P_1(n)C+P_2(n)C^2
=
y\,\partial_yR
+n\,y\,\frac{C'}C R,
\]

where

\[
\begin{aligned}
P_0(n)&=\frac{128}{3}(n+1)(2n+1)(2n+3)(3n+5),\\
P_1(n)&=-\frac8{27}(2n+3)(3n+2)
        (27n^2+81n+59),\\
P_2(n)&=\frac1{27}(n+2)(3n+2)(3n+4)(3n+5).
\end{aligned}
\]

Multiplication by \(C^n\) makes the right side

\[
y\frac d{dy}(RC^n),
\]

whose constant term is zero.  Thus

\[
P_0c_n+P_1c_{n+1}+P_2c_{n+2}=0.
\]

Combining this with the exact ratio for
\(b_n=\binom{3n}{2n}\) gives

\[
\boxed{
(n+1)^2A_{n+1}
-12(27n^2+27n+5)A_n
+2592(3n-2)(3n+2)A_{n-1}=0.
}
\]

For

\[
Y(t)=\sum_{n\ge0}A_nt^n,
\]

this recurrence is equivalent to

\[
\boxed{
t(108t-1)(216t-1)Y''
+(69984t^2-648t+1)Y'
+60(216t-1)Y=0.
}
\]

Finally, substituting \(E=32t\) in the Hamiltonian Picard--Fuchs equation
gives exactly this operator, coefficient by coefficient.

This is the isoperiodic conclusion:

\[
\text{Hamiltonian period}
=
\text{Laurent constant-term period}
\]

as analytic germs, because they satisfy the same second-order equation and
have the same normalized initial series.

---

## Files to use

- `figures/make_figures.py`  
  Produces the exact real and Abel--Wick figures in PNG, PDF, and SVG.

- `period_certificate/CERTIFICATE.txt`  
  Full scalar certificate function.

- `period_certificate/verify_scalar_certificate.py`  
  Exact proof that the certificate residual is zero modulo \(K-E\).

- `laurent/derive_and_verify_laurent.py`  
  Derives the Laurent recurrence, checks the rational certificate, computes
  coefficients, and verifies the common ODE.

- `laurent/certificate_R.txt`  
  The full Laurent telescoping certificate.

- `model_data.json`  
  Compact exact record of all formulas and normalizations.

- `run_all.py`  
  Runs every exact verification and regenerates every figure.

## Writing cautions

1. Do not conflate \(x=27E/4\) with \(t=E/32\).
2. Do not describe the left disk as a second minimum.  It surrounds a maximum,
   and its positive period is obtained by reversing cycle orientation.
3. Do not claim that the Laurent derivation is merely a finite coefficient
   match.  The rational telescoping certificate proves its recurrence.
4. Do not hide the fact that the period certificate is an identity on
   \(K=E\); state explicitly that the numerator reduces to zero modulo \(K-E\).
5. Use the bracket notation \([\,\cdot\,]_0\), not a named constant-term
   functional.
6. Keep the Hamiltonian model primary.  Do not replace it with a normal form.
