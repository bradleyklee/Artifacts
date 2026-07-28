
"""Exact map, triangle slice, cubic model, and closed Abel-Wick cycles."""

from __future__ import annotations
import math
import numpy as np

SQRT3 = math.sqrt(3.0)
A_CUBIC = 2.0 / (3.0 * SQRT3)

VERTICES = np.array([
    [0.0, 0.0, -0.25],
    [1.0, -1.5, 6.5],
    [-1.0, 1.5, 6.5],
])
CENTROID = np.array([0.0, 0.0, 4.25])
COMMON_IMAGE = np.array([-0.25, 0.0, 0.0])

STANDARD_CRITICAL = np.array([
    [SQRT3, 0.0],
    [-SQRT3 / 2.0, 1.5],
    [-SQRT3 / 2.0, -1.5],
])

COLORS = {"R": "#e31a1c", "G": "#169b3a", "Y": "#d9a300", "B": "#245cff"}
FAMILY_KEYS = ("G", "Y", "B")

AFFINE = np.linalg.lstsq(
    STANDARD_CRITICAL,
    VERTICES - CENTROID,
    rcond=None,
)[0].T

NORMAL = np.cross(VERTICES[1] - VERTICES[0], VERTICES[2] - VERTICES[0])
NORMAL /= np.linalg.norm(NORMAL)


def triangle_embedding(u, v):
    """The plane embedding iota(u,v) used in the paper."""
    u = np.asarray(u)
    v = np.asarray(v)
    return np.stack([
        u - v,
        -1.5 * (u - v),
        6.75 * (u + v) - 0.25,
    ], axis=-1)


def polynomial_map(points):
    """Levent Alpoge's polynomial map F=(P,Q,R), applied pointwise."""
    points = np.asarray(points, dtype=float)
    x, y, z = points[..., 0], points[..., 1], points[..., 2]
    xy = x * y
    return np.stack([
        (1 + xy) ** 3 * z + y * y * (1 + xy) * (4 + 3 * xy),
        y + 3 * x * (1 + xy) ** 2 * z + 3 * x * y * y * (4 + 3 * xy),
        2 * x - 3 * x * x * y - x ** 3 * z,
    ], axis=-1)


def triangle_map(u, v):
    """G=F composed with the triangle embedding."""
    return polynomial_map(triangle_embedding(u, v))


def H(u, v):
    """Triangle first integral H(u,v)=uv(1-u-v)."""
    return u * v * (1 - u - v)


def M(x, y):
    """Centered cubic level function from the paper."""
    return x*x + y*y + A_CUBIC * y * (y*y - 3*x*x)


def h3(p, q):
    """C3-symmetric elliptic model."""
    return p*p + q*q - A_CUBIC * (p**3 - 3*p*q*q)


def h_aw(p, q):
    """Abel-Wick continuation used for the auxiliary families."""
    return p*p - q*q - A_CUBIC * (p**3 + 3*p*q*q)


def embed_red(points):
    return CENTROID + np.asarray(points) @ AFFINE.T


def local_frame(index):
    ep = STANDARD_CRITICAL[index] / SQRT3
    eq = np.array([-ep[1], ep[0]])
    p_vector = AFFINE @ ep
    q_vector = np.linalg.norm(AFFINE @ eq) * NORMAL
    return p_vector, q_vector


def embed_aw(points, index):
    points = np.asarray(points)
    p_vector, q_vector = local_frame(index)
    return (
        CENTROID
        + points[:, 0, None] * p_vector
        + points[:, 1, None] * q_vector
    )


def c3_loop(alpha, samples=720):
    """Inner closed component h3(p,q)=alpha, 0<alpha<1."""
    theta = np.linspace(0, 2 * math.pi, samples)
    result = []
    for angle in theta:
        coeff = [-A_CUBIC * math.cos(3 * angle), 1.0, 0.0, -alpha]
        roots = np.roots(coeff)
        positive = sorted(
            float(r.real)
            for r in roots
            if abs(r.imag) < 1e-9 and r.real > 1e-10
        )
        if not positive:
            raise RuntimeError(f"no positive radial root at theta={angle}")
        radius = positive[0]
        result.append([radius * math.cos(angle), radius * math.sin(angle)])
    return np.asarray(result)


def aw_q_squared(p, beta):
    return (p*p - A_CUBIC*p**3 - beta) / (1 + 3*A_CUBIC*p)


def aw_closed_cycle(beta, samples=720):
    """Only the bounded real oval of h_aw(p,q)=beta."""
    roots = sorted(
        float(r.real)
        for r in np.roots([-A_CUBIC, 1.0, 0.0, -beta])
        if abs(r.imag) < 1e-9
    )
    _, inner, outer = roots
    half = max(240, samples // 2)
    p = np.linspace(inner, outer, half)
    q = np.sqrt(np.maximum(0.0, aw_q_squared(p, beta)))
    upper = np.column_stack([p, q])
    lower = np.column_stack([p[::-1], -q[::-1]])
    return np.vstack([upper, lower, upper[:1]])


def source_axis(index, samples=500):
    t = np.linspace(0, 1, samples)
    return CENTROID + t[:, None] * (VERTICES[index] - CENTROID)


def matched_point(alpha, index):
    roots = sorted(
        float(r.real)
        for r in np.roots([-A_CUBIC, 1.0, 0.0, -alpha])
        if abs(r.imag) < 1e-9 and 0 < r.real < SQRT3 + 1e-9
    )
    p_vector, _ = local_frame(index)
    return CENTROID + roots[0] * p_vector
