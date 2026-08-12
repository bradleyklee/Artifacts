# Trefoil symplectic-period artifact v2

Version 2 of the reproducible trefoil-period extraction.  It contains the
one-page certificate, exact SymPy verification, computed knot drawings,
independent numerical Hamiltonian checks, high-precision curved-surface area
quadrature, a secondary piecewise-flat mesh audit, and a separate real-space
algebraic trefoil geometry reconstructed in Python/SymPy.

## Primary geometry

The main certificate studies

```text
C = {z^2=w^3} subset C^2,
omega0 = (i/2)(dz ^ dbar(z) + dw ^ dbar(w)),
H = |z|^2 + |w|^2,
K_E = C intersect H^{-1}(E).
```

With

```text
z=s^3, w=s^2, s=sqrt(u) exp(i theta),
E=u^3+u^2,
```

the exact period is

```text
T(E) = pi (9u+4)/(3u+2).
```

The area-first formulation is

```text
A(E) = integral_{D_E} nu^*(omega0)
     = pi(3u^3+2u^2),
T(E) = dA/dE.
```

The singular cusp is handled on the normalization disk; the numerical curved
quadrature never evaluates at the singular point itself.

For

```text
Phi(E)=3-T(E)/pi,
```

the energy-native equations are

```text
(4-27E) Phi^3 - 12 Phi + 8 = 0,
E(27E-4) Phi'' + 2(27E-1) Phi' + 6 Phi = 0.
```

The value `E=4/27` is an algebraic/ODE branch value of the complexified
covering, not a positive real knot bifurcation.  On the real branch `u>0`,
`E(u)` and `T(u)` are smooth and strictly increasing.

Only at the series stage is the local uniformizer

```text
q=sqrt(E)/4
```

introduced.  It gives

```text
Phi(16q^2)=Sum (-1)^n a(n) q^n,
a(n)=4^n binom(3n/2,n),
```

with unsigned coefficients OEIS A244038.

## Validation stack

Run

```bash
./verify.sh
```

The verifier performs all of the following:

1. exact SymPy checks of the restricted forms, action, period, cubic, ODE,
   Gauss pullback, branch sign, integer expansion, and recurrence;
2. constrained Hamiltonian-flow quadrature directly on the curves in R^4;
3. polygonal Liouville-action differentiation;
4. curved radial-ring integration of the ambient symplectic 2-form using
   numerically estimated tangent vectors, without inserting the analytic
   pullback density;
5. numerical differentiation of those curved-surface areas back to the
   period;
6. a secondary piecewise-flat R^4 triangular-mesh convergence audit;
7. crossing/depth verification for all computed knot drawings;
8. the complete independent verification suite in
   `geometries/cyclic_R3_trefoil/`.

The curved-area audit currently agrees with the exact area at about `1e-11`
relative and recovers the period from numerical `dA/dE` at about `1e-10`
relative over the tested range.

## Comparison geometry

`geometries/cyclic_R3_trefoil/` is a standalone real-space comparison family.
It begins only from

```text
x(phi)=k sin(phi)+sin(2phi),
y(phi)=k cos(phi)-cos(2phi),
z(phi)=sin(3phi),
```

and reconstructs its two implicit surfaces by Laurent substitution and linear
coefficient matching.  No Groebner basis is used.  The exact period reduces to

```text
T(k)/pi = (1+k^2)/(k(1-k^2)^3 sqrt(k^2+4)),  0<k<1,
```

hence to the algebraic curve

```text
k^2(1-k^2)^6(k^2+4)(T/pi)^2-(1+k^2)^2=0.
```

Its actual period therefore has a minimal first-order linear ODE.  A valid
nonminimal second-order operator, factorization, and rational differential
certificate are also checked.  See that subfolder for the complete derivation.

## Build

```bash
./build.sh
```

This regenerates figures, reruns every verifier, rebuilds the LaTeX certificate,
runs PDF preflight, and rebuilds the comparison-family figures.

## File map

- `dist/trefoil_symplectic_period_certificate.pdf` - final certificate.
- `src/trefoil_certificate.tex` - LaTeX source.
- `src/verify_trefoil.py` - exact symbolic verifier.
- `src/numerical_audit.py` - constrained-flow and action audit.
- `src/curved_area_audit.py` - curved radial-ring symplectic-area audit.
- `src/mesh_area_audit.py` - secondary flat-triangle convergence audit.
- `src/make_figures.py` - computed knot-family and crossing figures.
- `src/trefoil_period_payload.json` - exact machine-readable payload.
- `geometries/cyclic_R3_trefoil/` - separate algebraic real-space trefoil
  reconstruction and verification suite.
- `MANIFEST.sha256` - checksums for the complete extraction.
