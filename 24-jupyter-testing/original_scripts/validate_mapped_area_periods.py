#!/usr/bin/env python3
"""Direct Gram quadrature and mapped-triangle mesh checks for four families.

The red routines extend ``recompute_true_surface_area.py``.  The green,
yellow, and blue routines use the local Abel-Wick maps from
``abel_wick_period_series.py``.  Potential poles are masked before division,
so this module runs cleanly with NumPy floating warnings promoted to errors.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import sympy as sp
from numpy.polynomial.legendre import leggauss

from compute_mesh_area_series import restricted_map_xy
import abel_wick_period_series as aw

SQRT3 = math.sqrt(3.0)
RED_CUBIC = 2.0 / (3.0 * SQRT3)


def safe_divide(numerator, denominator, *, fill=np.nan, where=None):
    """Broadcasting divide that never evaluates excluded entries."""
    numerator, denominator = np.broadcast_arrays(
        np.asarray(numerator, dtype=float),
        np.asarray(denominator, dtype=float),
    )
    if where is None:
        where = denominator != 0.0
    else:
        where = np.broadcast_to(np.asarray(where, dtype=bool), denominator.shape)
    output = np.full(denominator.shape, fill, dtype=float)
    np.divide(numerator, denominator, out=output, where=where)
    return output


def _stack_vector_output(values, target_shape):
    components = [
        np.broadcast_to(np.asarray(value, dtype=float), target_shape)
        for value in values
    ]
    return np.stack(components, axis=-1)


# ---------------------------------------------------------------------------
# Red family
# ---------------------------------------------------------------------------

def red_uv_from_xy(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return (
        1 / 3 + x / 3 + y / (3 * SQRT3),
        1 / 3 - x / 3 + y / (3 * SQRT3),
    )


def red_range_map(x, y):
    """Restricted polynomial map in the paper's centered harmonic coordinates."""
    u, v = red_uv_from_xy(x, y)
    difference = u - v
    total = u + v
    P = -(3 * difference**2 - 2) * (
        243 * difference**4 * total
        - 171 * difference**4
        - 324 * difference**2 * total
        + 156 * difference**2
        + 108 * total
        - 4
    ) / 32.0
    Q = 9 * difference * (
        81 * difference**4 * total
        - 57 * difference**4
        - 108 * difference**2 * total
        + 52 * difference**2
        + 36 * total
        - 4
    ) / 16.0
    R = -difference * (27 * difference**2 * total - 19 * difference**2 - 8) / 4.0
    return np.stack([P, Q, R], axis=-1)


@lru_cache(None)
def _red_cross_function():
    x, y = sp.symbols("x y", real=True)
    P, Q, R = restricted_map_xy()
    rx = sp.Matrix([sp.diff(P, x), sp.diff(Q, x), sp.diff(R, x)])
    ry = sp.Matrix([sp.diff(P, y), sp.diff(Q, y), sp.diff(R, y)])
    return sp.lambdify((x, y), tuple(sp.expand(rx.cross(ry))), "numpy")


def red_density(x, y):
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    cross = _stack_vector_output(_red_cross_function()(x, y), x.shape)
    return np.linalg.norm(cross, axis=-1)


def red_center_density() -> float:
    return float(red_density(0.0, 0.0))


def red_radial_triangle_boundary(theta):
    """Distance from the centered cubic point to the triangle boundary."""
    theta = np.asarray(theta, dtype=float)
    cosine = np.cos(theta)
    sine = np.sin(theta)

    first_denominator = cosine + sine / SQRT3
    first = np.full_like(first_denominator, np.inf)
    np.divide(-1.0, first_denominator, out=first, where=first_denominator < 0.0)

    second_denominator = -cosine + sine / SQRT3
    second = np.full_like(second_denominator, np.inf)
    np.divide(-1.0, second_denominator, out=second, where=second_denominator < 0.0)

    third = np.full_like(sine, np.inf)
    np.divide(SQRT3, 2.0 * sine, out=third, where=sine > 0.0)
    boundary = np.minimum.reduce((first, second, third))
    if not np.all(np.isfinite(boundary)):
        raise FloatingPointError("nonfinite red triangle boundary")
    return boundary


def red_level(radius, theta):
    return radius**2 - RED_CUBIC * radius**3 * np.sin(3.0 * theta)


def red_boundary_radius(level: float, theta):
    theta = np.asarray(theta, dtype=float)
    lower = np.zeros_like(theta)
    upper = red_radial_triangle_boundary(theta)
    for _ in range(72):
        midpoint = 0.5 * (lower + upper)
        below = red_level(midpoint, theta) < level
        lower[below] = midpoint[below]
        upper[~below] = midpoint[~below]
    return 0.5 * (lower + upper)


def red_direct_quadrature(level: float, ntheta=280, nrho=80):
    return _direct_quadrature(red_density, red_boundary_radius, level, ntheta, nrho)


# ---------------------------------------------------------------------------
# Abel-Wick green/yellow/blue families
# ---------------------------------------------------------------------------
@lru_cache(None)
def _aw_numeric_family(family: int):
    range_map = aw.local_range_map(family)
    rx = range_map.diff(aw.X)
    ry = range_map.diff(aw.Y)
    cross = sp.expand(rx.cross(ry))
    range_function = sp.lambdify((aw.X, aw.Y), tuple(range_map), "numpy")
    cross_function = sp.lambdify((aw.X, aw.Y), tuple(cross), "numpy")
    center_squared = sp.factor(cross.dot(cross).subs({aw.X: 0, aw.Y: 0}))
    return range_function, cross_function, float(sp.sqrt(center_squared))


def aw_range_map(family: int, x, y):
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    range_function, _, _ = _aw_numeric_family(family)
    return _stack_vector_output(range_function(x, y), x.shape)


def aw_density(family: int, x, y):
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    _, cross_function, _ = _aw_numeric_family(family)
    cross = _stack_vector_output(cross_function(x, y), x.shape)
    return np.linalg.norm(cross, axis=-1)


def aw_center_density(family: int) -> float:
    return _aw_numeric_family(family)[2]


def aw_boundary_radius(level: float, theta):
    """Small bounded root of r^2+a cos(theta) r^3=level."""
    theta = np.asarray(theta, dtype=float)
    cosine = np.cos(theta)
    cubic = float(aw.A_CUBIC)
    lower = np.zeros_like(cosine)
    upper = np.full_like(cosine, max(1.0, 2.0 * math.sqrt(level)))

    nonnegative = cosine >= 0.0
    upper[nonnegative] = math.sqrt(level)

    negative = ~nonnegative
    if np.any(negative):
        c = cosine[negative]
        radial_maximum = safe_divide(-2.0, 3.0 * cubic * c, where=c < 0.0)
        trial = np.minimum(upper[negative], 0.999999 * radial_maximum)
        values = trial**2 + cubic * c * trial**3
        for _ in range(80):
            need_larger = values < level
            if not np.any(need_larger):
                break
            trial[need_larger] = np.minimum(
                2.0 * trial[need_larger],
                0.999999 * radial_maximum[need_larger],
            )
            values = trial**2 + cubic * c * trial**3
        if np.any(values < level):
            raise ValueError("level lies outside the bounded Abel-Wick lobe")
        upper[negative] = trial

    for _ in range(72):
        midpoint = 0.5 * (lower + upper)
        below = midpoint**2 + cubic * cosine * midpoint**3 < level
        lower[below] = midpoint[below]
        upper[~below] = midpoint[~below]
    return 0.5 * (lower + upper)


def aw_direct_quadrature(family: int, level: float, ntheta=280, nrho=80):
    return _direct_quadrature(
        lambda x, y: aw_density(family, x, y),
        aw_boundary_radius,
        level,
        ntheta,
        nrho,
    )


# ---------------------------------------------------------------------------
# Shared quadrature and mesh machinery
# ---------------------------------------------------------------------------

def _direct_quadrature(density, boundary, level, ntheta, nrho):
    theta_nodes, theta_weights = leggauss(ntheta)
    theta = math.pi * (theta_nodes + 1.0)
    theta_weights = math.pi * theta_weights

    radial_nodes, radial_weights = leggauss(nrho)
    fraction = 0.5 * (radial_nodes + 1.0)
    radial_weights = 0.5 * radial_weights

    radius = boundary(level, theta)
    r = fraction[:, None] * radius[None, :]
    x = r * np.cos(theta)[None, :]
    y = r * np.sin(theta)[None, :]
    integrand = density(x, y) * fraction[:, None] * radius[None, :] ** 2
    return float(
        np.sum(integrand * radial_weights[:, None] * theta_weights[None, :])
    )


def _structured_mesh(range_function, boundary_function, level, nr, ntheta):
    theta = np.linspace(0.0, 2.0 * math.pi, ntheta, endpoint=False)
    radius = boundary_function(level, theta)

    domain = [np.array([0.0, 0.0])]
    vertices = [np.asarray(range_function(0.0, 0.0), dtype=float)]
    for ring in range(1, nr + 1):
        fraction = ring / nr
        r = fraction * radius
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        domain.extend(np.column_stack([x, y]))
        vertices.extend(np.asarray(range_function(x, y), dtype=float))

    triangles = []
    for k in range(ntheta):
        triangles.append((0, 1 + k, 1 + (k + 1) % ntheta))
    for ring in range(1, nr):
        inner = 1 + (ring - 1) * ntheta
        outer = 1 + ring * ntheta
        for k in range(ntheta):
            next_k = (k + 1) % ntheta
            triangles.append((inner + k, outer + k, outer + next_k))
            triangles.append((inner + k, outer + next_k, inner + next_k))

    return (
        np.asarray(domain),
        np.asarray(vertices),
        np.asarray(triangles, dtype=int),
    )


def red_structured_mesh(level: float, nr=24, ntheta=96):
    return _structured_mesh(red_range_map, red_boundary_radius, level, nr, ntheta)


def aw_structured_mesh(family: int, level: float, nr=24, ntheta=96):
    return _structured_mesh(
        lambda x, y: aw_range_map(family, x, y),
        aw_boundary_radius,
        level,
        nr,
        ntheta,
    )


def mesh_area(vertices, triangles):
    first = vertices[triangles[:, 0]]
    second = vertices[triangles[:, 1]]
    third = vertices[triangles[:, 2]]
    return float(
        0.5 * np.linalg.norm(np.cross(second - first, third - first), axis=1).sum()
    )


def main() -> None:
    old = np.seterr(divide="raise", invalid="raise", over="raise", under="ignore")
    try:
        print("red", red_direct_quadrature(0.1, 80, 30))
        for family, level in ((0, 0.02), (1, 0.002), (2, 0.002)):
            print(aw.FAMILY_NAMES[family], aw_direct_quadrature(family, level, 80, 30))
        print("PASS: no divide/invalid/overflow warning")
    finally:
        np.seterr(**old)


if __name__ == "__main__":
    main()
