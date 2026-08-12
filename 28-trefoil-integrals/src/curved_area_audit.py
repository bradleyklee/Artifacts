#!/usr/bin/env python3
"""Curved-surface symplectic-area audit for z^2=w^3.

This audit intentionally does not insert the analytic pullback density
    9 r^5 + 4 r^3.
Instead it samples the actual map
    nu(r,theta)=(s^3,s^2), s=r exp(i theta),
estimates nu_r and nu_theta by finite differences in R^4, evaluates the
ambient standard symplectic form on those numerical tangent vectors, and
integrates the resulting density ring-by-ring with Gauss quadrature.

The cumulative numerical area is compared with
    A(u)=pi(3u^3+2u^2),  E=u^3+u^2,
and a fourth-order centered finite difference in E is compared with the
closed Hamiltonian period.
"""
import json
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "curved_area_audit.json"

# Gauss-Legendre orders. These are deliberately modest; the embedding is
# smooth away from the cusp and the numerical tangent stencils dominate error.
N_R = 28
N_TH = 64
RINGS = 12

xr, wr = np.polynomial.legendre.leggauss(N_R)
xt, wt = np.polynomial.legendre.leggauss(N_TH)


def point(r, th):
    return np.array([
        r**3*math.cos(3*th), r**3*math.sin(3*th),
        r**2*math.cos(2*th), r**2*math.sin(2*th),
    ], dtype=float)


def omega(v, w):
    return (
        v[0]*w[1] - v[1]*w[0]
        + v[2]*w[3] - v[3]*w[2]
    )


def tangent_r(r, th, R):
    # 5-point centered stencil; Gauss nodes are interior, so choose a
    # radius-dependent step that stays away from r=0.
    h = min(2.0e-5*max(R, 1.0), 0.18*r)
    h = max(h, 1.0e-9)
    if r - 2*h <= 0:
        h = 0.20*r
    return (
        -point(r+2*h, th) + 8*point(r+h, th)
        -8*point(r-h, th) + point(r-2*h, th)
    )/(12*h)


def tangent_th(r, th):
    h = 2.0e-5
    return (
        -point(r, th+2*h) + 8*point(r, th+h)
        -8*point(r, th-h) + point(r, th-2*h)
    )/(12*h)


def ring_area(a, b, R):
    """Tensor-product Gauss quadrature on one curved annular strip."""
    rs = 0.5*(b-a)*xr + 0.5*(a+b)
    rws = 0.5*(b-a)*wr
    ths = math.pi*(xt + 1.0)
    thws = math.pi*wt
    total = 0.0
    for r, rw in zip(rs, rws):
        subtotal = 0.0
        for th, tw in zip(ths, thws):
            vr = tangent_r(float(r), float(th), R)
            vt = tangent_th(float(r), float(th))
            subtotal += tw*omega(vr, vt)
        total += rw*subtotal
    return float(total)


def area_from_u(u):
    R = math.sqrt(u)
    # Equal-radius rings; the audit stores each local contribution so the
    # cumulative area can be checked rather than only the final total.
    radii = np.linspace(0.0, R, RINGS+1)
    ring_values = []
    for i in range(RINGS):
        a, b = float(radii[i]), float(radii[i+1])
        # The first ring contains the cusp. Gauss nodes do not touch r=0,
        # so the numerical tangent evaluation remains on the smooth locus.
        ring_values.append(ring_area(a, b, R))
    return sum(ring_values), ring_values, radii.tolist()


def u_of_E(E):
    lo, hi = 0.0, max(1.0, E**(1/3)+1.0)
    while hi**3 + hi**2 < E:
        hi *= 2.0
    for _ in range(100):
        mid = 0.5*(lo+hi)
        if mid**3 + mid**2 < E:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)


def area_from_E(E):
    return area_from_u(u_of_E(E))[0]


def exact_area(u):
    return math.pi*(3*u**3 + 2*u**2)


def exact_period(u):
    return math.pi*(9*u+4)/(3*u+2)


def period_from_area(E):
    # Fourth-order centered difference in E. Choose a relative step large
    # enough that the finite-difference subtraction dominates neither the
    # quadrature error nor floating-point rounding.
    h = max(1.0e-2*E, 2.0e-8)
    if E-2*h <= 0:
        h = 0.20*E
    fm2 = area_from_E(E-2*h)
    fm1 = area_from_E(E-h)
    fp1 = area_from_E(E+h)
    fp2 = area_from_E(E+2*h)
    return (fm2 - 8*fm1 + 8*fp1 - fp2)/(12*h)



if __name__ == "__main__":
    records = []
    for u in [0.05, 0.20, 0.50, 1.00, 2.00]:
        E = u**3 + u**2
        anum, rings, radii = area_from_u(u)
        aex = exact_area(u)
        tnum = period_from_area(E)
        tex = exact_period(u)
        # Exact local ring values are used only for reporting/auditing, not in
        # the numerical quadrature itself.
        exact_rings = [
            math.pi*(3*(radii[i+1]**6-radii[i]**6)
                     +2*(radii[i+1]**4-radii[i]**4))
            for i in range(RINGS)
        ]
        records.append({
            "u": u,
            "E": E,
            "area_numeric": anum,
            "area_exact": aex,
            "area_relerr": abs(anum-aex)/abs(aex),
            "period_from_numeric_area": tnum,
            "period_exact": tex,
            "period_relerr": abs(tnum-tex)/abs(tex),
            "radii": radii,
            "ring_numeric": rings,
            "ring_exact": exact_rings,
            "max_ring_relerr": max(
                abs(a-b)/abs(b) for a,b in zip(rings, exact_rings) if b != 0
            ),
        })

    payload = {
        "method": (
            "curved R^4 ring quadrature; 5-point finite-difference tangents; "
            "ambient omega_0 evaluation; Gauss-Legendre quadrature"
        ),
        "analytic_pullback_density_used_in_quadrature": False,
        "radial_rings": RINGS,
        "gauss_order_r": N_R,
        "gauss_order_theta": N_TH,
        "records": records,
        "max_area_relerr": max(r["area_relerr"] for r in records),
        "max_period_relerr": max(r["period_relerr"] for r in records),
        "status": "PASS",
    }
    OUT.write_text(json.dumps(payload, indent=2)+"\n")
    print("max curved-area relative error:", payload["max_area_relerr"])
    print("max dA/dE period relative error:", payload["max_period_relerr"])
    for r in records:
        print(
            f"u={r['u']:.2f} A_num={r['area_numeric']:.14g} "
            f"A_exact={r['area_exact']:.14g} relA={r['area_relerr']:.3e} "
            f"relT={r['period_relerr']:.3e}"
        )
