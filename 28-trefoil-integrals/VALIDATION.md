# Validation notes

## Curved-area audit

The high-precision area check uses the actual map

```text
nu(r,theta)=(r^3 exp(3i theta), r^2 exp(2i theta)) in R^4.
```

At Gauss quadrature nodes, `nu_r` and `nu_theta` are estimated numerically by
five-point finite differences.  The code then evaluates

```text
omega0(nu_r,nu_theta)
```

directly and sums annular contributions radially outward.  The analytic
Jacobian/pullback density is not supplied to the quadrature routine.  Local
ring totals, cumulative totals, and the final exact area are all retained in
`src/curved_area_audit.json`.

A fourth-order centered finite difference in `E` is then applied to the
independently computed curved areas.  This recovers the exact Hamiltonian
period to about `1e-10` relative on the validation set.

## Flat-mesh audit

`src/mesh_area_audit.py` maps a triangulated normalization disk into R^4 and
integrates the constant ambient symplectic form exactly over each flat
triangle.  It is intentionally kept as a separate geometric convergence
check rather than the headline precision test.  Angular refinement shows the
expected second-order chordal convergence.  Changing the interior radial
triangulation while keeping the same polygonal boundary leaves the discrete
symplectic chain integral unchanged to floating-point precision, as expected
from exactness and cancellation of internal edges.

## Independent Hamiltonian audit

`src/numerical_audit.py` does not use the closed time form.  It estimates the
tangent plane numerically in R^4, solves the constrained Hamiltonian equation
there, and integrates the resulting `dt/dtheta`.  It also computes a separate
polygonal Liouville action and differentiates it in energy.
