#!/usr/bin/env python3
"""Numerical inductive period data for even sphere curves.

This front end follows the same chart as even_sphere_quartic_factory.py.  It is
for discovery and cross-checking; exact certification belongs to the quotient
reducer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import sympy as sp
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.polynomial import polyfit, polyval

from even_sphere_quartic_factory import alpha, u, v


@dataclass
class PeriodSample:
    alpha: float
    period: float
    min_u: float
    max_u: float


def _quadratic_coefficients(F: sp.Expr):
    p = sp.Poly(F, u)
    if p.degree() > 2:
        raise ValueError("quartic-in-J input must give degree <=2 in u")
    cs = [sp.S(0)]*(3-len(p.all_coeffs()))+p.all_coeffs()
    return [sp.lambdify((v, alpha), q, "numpy") for q in cs]


def period_on_polar_branch(F: sp.Expr, energy: float, nodes: int = 768) -> PeriodSample:
    """Integrate the positive-Jz branch continuously connected to u=1."""
    funcs = _quadratic_coefficients(F)
    x, w = leggauss(nodes)
    phi = np.pi*(x+1.0)              # [0,2pi]
    weights = np.pi*w
    vv = np.cos(phi)**2
    aa, bb, cc = [np.broadcast_to(np.asarray(f(vv, energy), float), vv.shape) for f in funcs]
    roots = np.empty((2, nodes), dtype=np.complex128)
    linear = np.abs(aa) < 1e-13
    roots[:, linear] = np.vstack((-cc[linear]/bb[linear], -cc[linear]/bb[linear]))
    disc = bb[~linear]**2-4*aa[~linear]*cc[~linear]
    sd = np.sqrt(disc.astype(np.complex128))
    roots[0, ~linear] = (-bb[~linear]+sd)/(2*aa[~linear])
    roots[1, ~linear] = (-bb[~linear]-sd)/(2*aa[~linear])
    choose = np.argmin(np.abs(roots-1), axis=0)
    uu = roots[choose, np.arange(nodes)]
    if np.max(np.abs(uu.imag)) > 2e-9 or np.min(uu.real) <= 0 or np.max(uu.real) > 1+2e-8:
        raise ValueError("requested energy is not a regular real polar branch")
    uu = uu.real
    Fu = 2*aa*uu+bb
    integrand = 1/(2*np.sqrt(uu)*Fu)
    period = float(np.dot(weights, integrand))
    return PeriodSample(energy, period, float(uu.min()), float(uu.max()))


def local_period_series(
    F: sp.Expr,
    critical_energy: float,
    beta_max: float,
    degree: int = 8,
    sample_count: int = 24,
    nodes: int = 768,
) -> dict:
    """Fit T(alpha0-beta)=sum c_n beta^n and report held-out residuals."""
    beta = np.linspace(beta_max/(sample_count+2), beta_max, sample_count)
    vals = np.array([period_on_polar_branch(F, critical_energy-b, nodes).period for b in beta])
    coeff = polyfit(beta, vals, degree)
    hold = beta_max*np.array([0.031,0.173,0.419,0.733,0.947])
    truth = np.array([period_on_polar_branch(F, critical_energy-b, nodes).period for b in hold])
    pred = polyval(hold, coeff)
    return {
        "critical_energy": critical_energy,
        "variable": "beta=critical_energy-alpha",
        "coefficients_low_to_high": coeff.tolist(),
        "beta_max": beta_max,
        "sample_count": sample_count,
        "quadrature_nodes": nodes,
        "heldout_max_abs_residual": float(np.max(np.abs(truth-pred))),
        "heldout_max_rel_residual": float(np.max(np.abs((truth-pred)/truth))),
    }

