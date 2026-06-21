#!/usr/bin/env python3
"""Independent floating-point cross-check of the exact ellipse binary through n=10.

The C++ program remains the deciding exact computation.  This script regenerates
free polyominoes, runs SciPy/HiGHS on the normalized coefficient LP, parses the
C++ exact witness list, and compares accepted canonical shape sets.
"""
from __future__ import annotations

import re
import subprocess
import sys
from itertools import product
from math import gcd
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.optimize import linprog

Point = tuple[int, int]
Poly = tuple[Point, ...]
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def normalize(points: Iterable[Point]) -> Poly:
    pts = list(points)
    min_x = min(x for x, _ in pts)
    min_y = min(y for _, y in pts)
    return tuple(sorted((x - min_x, y - min_y) for x, y in pts))


def canonical(poly: Poly) -> Poly:
    images: list[Poly] = []
    for t in range(8):
        image: list[Point] = []
        for x, y in poly:
            transforms = ((x, y), (x, -y), (-x, y), (-x, -y),
                          (y, x), (y, -x), (-y, x), (-y, -x))
            image.append(transforms[t])
        images.append(normalize(image))
    return min(images)


def add_one(parents: set[Poly]) -> set[Poly]:
    children: set[Poly] = set()
    for poly in parents:
        occupied = set(poly)
        for x, y in poly:
            for dx, dy in DIRECTIONS:
                q = (x + dx, y + dy)
                if q not in occupied:
                    children.add(canonical(tuple((*poly, q))))
    return children


def cross(o: Point, a: Point, b: Point) -> int:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(poly: Poly) -> list[Point]:
    pts = sorted(set(poly))
    if len(pts) <= 1:
        return pts
    lower: list[Point] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def hull_lattice_count(h: list[Point]) -> int:
    if len(h) <= 1:
        return len(h)
    if len(h) == 2:
        return gcd(abs(h[1][0] - h[0][0]), abs(h[1][1] - h[0][1])) + 1
    twice_area = 0
    boundary = 0
    for a, b in zip(h, h[1:] + h[:1]):
        twice_area += a[0] * b[1] - a[1] * b[0]
        boundary += gcd(abs(b[0] - a[0]), abs(b[1] - a[1]))
    return (abs(twice_area) + boundary + 2) // 2


def immediate_exterior(poly: Poly) -> list[Point]:
    occupied = set(poly)
    return sorted({(x + dx, y + dy) for x, y in poly for dx, dy in DIRECTIONS
                   if (x + dx, y + dy) not in occupied})


def scipy_accepts(poly: Poly) -> bool:
    h = hull(poly)
    if hull_lattice_count(h) != len(poly):
        return False
    exterior = immediate_exterior(poly)
    # Variables: A, C+, C-, D+, D-, E+, E-, eps.  All non-negative.
    A_ub: list[list[float]] = []
    b_ub: list[float] = []
    A_ub += [[-1, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1]]
    b_ub += [0, 1]
    for x, y in h:
        delta = x*x - y*y
        A_ub.append([delta, x, -x, y, -y, 1, -1, 0])
        b_ub.append(-y*y)
    for x, y in exterior:
        delta = x*x - y*y
        A_ub.append([-delta, -x, x, -y, y, -1, 1, 1])
        b_ub.append(y*y)
    result = linprog(
        c=[0, 0, 0, 0, 0, 0, 0, -1],
        A_ub=np.asarray(A_ub, dtype=float),
        b_ub=np.asarray(b_ub, dtype=float),
        bounds=[(0, None)] * 8,
        method="highs",
    )
    return bool(result.success and result.x[7] > 1e-8)


def parse_cpp_witnesses(text: str) -> dict[int, set[Poly]]:
    out: dict[int, set[Poly]] = {}
    pat = re.compile(r"^  witness n=(\d+) P=(.*?) A=", re.MULTILINE)
    point_pat = re.compile(r"\((-?\d+),(-?\d+)\)")
    for n_text, sites in pat.findall(text):
        poly = tuple(sorted((int(x), int(y)) for x, y in point_pat.findall(sites)))
        out.setdefault(int(n_text), set()).add(canonical(poly))
    return out


def main() -> None:
    binary = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./ellipse_polyomino")).resolve()
    output = subprocess.check_output([str(binary), "--max-n", "10", "--dump-witnesses"], text=True)
    cpp = parse_cpp_witnesses(output)

    levels: dict[int, set[Poly]] = {1: {((0, 0),)}}
    for n in range(2, 11):
        levels[n] = add_one(levels[n - 1])

    total = 0
    for n in range(1, 11):
        scipy_shapes = {poly for poly in levels[n] if scipy_accepts(poly)}
        exact_shapes = cpp.get(n, set())
        if scipy_shapes != exact_shapes:
            only_scipy = sorted(scipy_shapes - exact_shapes)
            only_exact = sorted(exact_shapes - scipy_shapes)
            raise SystemExit(
                f"mismatch at n={n}: scipy-only={only_scipy[:2]} exact-only={only_exact[:2]}"
            )
        total += len(scipy_shapes)
        print(f"n={n:2d}: {len(scipy_shapes):2d} accepted shapes agree")
    print(f"PASS: SciPy/HiGHS and exact C++ agree shape-for-shape through n=10 ({total} accepted shapes).")


if __name__ == "__main__":
    main()
