# ALG-007: sphere-curve action/period certificate branch

```text
INPUT:
  polynomial or finite spherical-harmonic Hamiltonian H(Jx,Jy,Jz)
  axis u and oriented real/complex cycle family C_u(alpha)
  energy convention alpha = H

ASSERT:
  Jx^2 + Jy^2 + Jz^2 = 1                 (real sphere branch)
  or the declared Abel-Wick quadratic constraint (complex branch)

CHART:
  lambda := J_u
  choose transverse coordinates
    J_v := sqrt(1-lambda^2) cos(phi)
    J_w := sqrt(1-lambda^2) sin(phi)
  F := H(lambda,phi) - alpha

VERIFY CANONICAL SIGN:
  dot(lambda) = -partial_phi H
  dot(phi)    =  partial_lambda H

BUILD DIFFERENTIALS:
  action differential eta := lambda dphi
  period differential tau := dphi / partial_lambda(H)
  verify on F=0 that partial_alpha(eta) = tau

ALGEBRAIZE ANGLE:
  u := cos(phi), v := sin(phi)
  add relation u^2 + v^2 - 1 = 0
  retain enough branch data to preserve contour orientation

INDUCTIVE PASS:
  expand local lambda(alpha,phi)
  integrate coefficient functions around C_u
  guess A = sum_k P_k(alpha) D_alpha^k

REDUCTIVE PASS:
  compute tau, D_alpha(tau), ..., D_alpha^r(tau)
  reduce in quotient <F, u^2+v^2-1>
  construct exact-image columns d_phi(Xi)
  solve C*x + W*a = 0

DEDUCTIVE VERIFY:
  reconstruct exact coefficients
  verify A(tau) - d_phi(Xi) = 0 in the quotient
  integrate around each declared complete cycle

OUTPUT:
  normalization record
  operator A
  primitive Xi
  exact quotient audit
  real/complex cycle definitions and initial data
  singular-energy and local-exponent data
```

Do not infer a universal source bound from the plane quartic bound `6r-3`.
The sphere branch needs its own bound, plausibly graded by spherical-harmonic
degree and pole order.

