
"""Pre-image area, image-area density, shell integrals, and series helpers."""

from __future__ import annotations
import math
import numpy as np
import mpmath as mp
import sympy as sp

SQRT3 = math.sqrt(3.0)
A_CUBIC = 2.0 / (3.0 * SQRT3)
J_CENTER = math.sqrt(6267.0) / 4.0


def F3(m):
    return mp.hyper([mp.mpf(1)/3, mp.mpf(2)/3], [1], m)


def S3(m):
    return m * mp.hyper([mp.mpf(1)/3, mp.mpf(2)/3], [2], m)


def preimage_area(m):
    """A_0(m)=2*pi*sqrt(3)/27*S_3(m)."""
    return 2 * mp.pi * mp.sqrt(3) / 27 * S3(m)


def preimage_action(m):
    return preimage_area(m) / (2 * mp.pi)


def centered_to_triangle(x, y):
    u = mp.mpf(1)/3 + x/3 + y/(3*mp.sqrt(3))
    v = mp.mpf(1)/3 - x/3 + y/(3*mp.sqrt(3))
    return u, v


def radial_boundary(theta):
    """Positive radius at m=1 for the cubic triangle boundary."""
    s = mp.sin(3 * theta)
    if abs(s) < mp.mpf("1e-25"):
        return mp.mpf(1)
    # Solve r^2 - a r^3 sin(3theta)=1 and choose the smallest positive root.
    coeff = [-A_CUBIC * s, 1, 0, -1]
    roots = mp.polyroots(coeff, maxsteps=100)
    positive = sorted(mp.re(r) for r in roots if abs(mp.im(r)) < 1e-20 and mp.re(r) > 0)
    return positive[0]


def boundary_radius(m, theta):
    """Positive inner root R_m(theta)."""
    s = mp.sin(3 * theta)
    f = lambda r: r*r - A_CUBIC*r**3*s - m
    hi = radial_boundary(theta)
    return mp.findroot(f, (mp.sqrt(m) * mp.mpf("0.8"), min(hi, mp.sqrt(m) * mp.mpf("1.4") + mp.mpf("0.1"))))


def _restricted_map_symbolic():
    x, y = sp.symbols("x y", real=True)
    u = sp.Rational(1, 3) + x/sp.Integer(3) + y/(3*sp.sqrt(3))
    v = sp.Rational(1, 3) - x/sp.Integer(3) + y/(3*sp.sqrt(3))
    X = u-v
    Y = -sp.Rational(3,2)*(u-v)
    Z = sp.Rational(27,4)*(u+v)-sp.Rational(1,4)
    xy = X*Y
    P = (1+xy)**3*Z + Y**2*(1+xy)*(4+3*xy)
    Q = Y + 3*X*(1+xy)**2*Z + 3*X*Y**2*(4+3*xy)
    R = 2*X - 3*X**2*Y - X**3*Z
    return x, y, sp.Matrix([sp.expand(P), sp.expand(Q), sp.expand(R)])


_X, _Y, _G = _restricted_map_symbolic()
_GX = _G.diff(_X)
_GY = _G.diff(_Y)
_CROSS = sp.simplify(_GX.cross(_GY))
_DENSITY_SQUARED = sp.expand(sum(c*c for c in _CROSS))
_DENSITY = sp.lambdify((_X, _Y), sp.sqrt(_DENSITY_SQUARED), "numpy")


def intrinsic_cross_product():
    return _CROSS


def intrinsic_density_squared():
    return _DENSITY_SQUARED


def image_area_density(x, y):
    return _DENSITY(x, y)


def image_area_quadrature(m, ntheta=320, nrho=90):
    """Direct tensor-product quadrature of the exact density over D_m."""
    theta_nodes, theta_weights = np.polynomial.legendre.leggauss(ntheta)
    rho_nodes, rho_weights = np.polynomial.legendre.leggauss(nrho)
    thetas = math.pi * (theta_nodes + 1)
    tw = math.pi * theta_weights
    total = 0.0
    for theta, wt in zip(thetas, tw):
        R = float(boundary_radius(m, theta))
        rho = 0.5 * R * (rho_nodes + 1)
        rw = 0.5 * R * rho_weights
        x = rho * math.cos(theta)
        y = rho * math.sin(theta)
        total += wt * np.sum(rw * image_area_density(x, y) * rho)
    return float(total)


def normalized_image_area(m, **kwargs):
    return image_area_quadrature(m, **kwargs) / (math.pi * J_CENTER)
