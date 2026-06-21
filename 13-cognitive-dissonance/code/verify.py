#!/usr/bin/env python3
"""Exact verifier for the N=18 unit-square and N=45 site-set disk witnesses.

All membership tests use fractions.Fraction; floating point is never used in
verification.  For rendering, the companion renderer converts already-checked
values to floats only after these exact checks have passed.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

Point = tuple[int, int]
RPoint = tuple[Fraction, Fraction]


def F(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def fpair(values: list[str] | tuple[str, str]) -> RPoint:
    return (F(values[0]), F(values[1]))


def sqdist(p: tuple[int | Fraction, int | Fraction], c: RPoint) -> Fraction:
    return (F(p[0]) - c[0]) ** 2 + (F(p[1]) - c[1]) ** 2


def ceil_sqrt_fraction(q: Fraction) -> int:
    """Return the least integer k with k^2 >= q, using exact comparisons."""
    if q < 0:
        raise ValueError("square root of negative rational")
    k = math.isqrt(q.numerator // q.denominator)
    while Fraction(k * k) < q:
        k += 1
    return k


def disk_box(center: RPoint, r2: Fraction, pad: int = 1) -> tuple[int, int, int, int]:
    """A certified finite box containing every integer point in the closed disk."""
    k = ceil_sqrt_fraction(r2)
    x0 = math.floor(center[0]) - k - pad
    x1 = math.floor(center[0]) + k + pad
    y0 = math.floor(center[1]) - k - pad
    y1 = math.floor(center[1]) + k + pad
    return x0, x1, y0, y1


def disk_lattice_points(center: RPoint, r2: Fraction) -> tuple[set[Point], tuple[int, int, int, int]]:
    x0, x1, y0, y1 = disk_box(center, r2)
    points = {
        (x, y)
        for x in range(x0, x1 + 1)
        for y in range(y0, y1 + 1)
        if sqdist((x, y), center) <= r2
    }
    return points, (x0, x1, y0, y1)


def cells_to_vertices(cells: Iterable[Point]) -> set[Point]:
    vertices: set[Point] = set()
    for i, j in cells:
        vertices.update(((i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)))
    return vertices


def induced_cells_from_vertices(vertices: set[Point], box: tuple[int, int, int, int]) -> set[Point]:
    """All lower-left cells whose four vertices are in the closed disk.

    A disk is convex, so this four-corner test is equivalent to containment of
    the entire unit square in the disk.
    """
    x0, x1, y0, y1 = box
    return {
        (i, j)
        for i in range(x0, x1)
        for j in range(y0, y1)
        if {(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)} <= vertices
    }


def centroid(points: set[Point]) -> RPoint:
    n = len(points)
    return (sum(F(x) for x, _ in points) / n, sum(F(y) for _, y in points) / n)


def norm_d4(points: set[Point]) -> tuple[Point, ...]:
    """Canonical translation-normalized D4 image of an integer-site pattern."""
    transforms = (
        lambda x, y: (x, y),
        lambda x, y: (x, -y),
        lambda x, y: (-x, y),
        lambda x, y: (-x, -y),
        lambda x, y: (y, x),
        lambda x, y: (y, -x),
        lambda x, y: (-y, x),
        lambda x, y: (-y, -x),
    )
    images = []
    for transform in transforms:
        image = [transform(x, y) for x, y in points]
        dx = min(x for x, _ in image)
        dy = min(y for _, y in image)
        images.append(tuple(sorted((x - dx, y - dy) for x, y in image)))
    return min(images)


@dataclass(frozen=True)
class N18Record:
    ident: str
    center: RPoint  # standard lower-left-corner coordinate convention
    r2: Fraction
    cells: frozenset[Point]
    vertices: frozenset[Point]
    disk_vertices: frozenset[Point]
    strict_vertices: int
    boundary_vertices: int
    induced_cells: frozenset[Point]
    box: tuple[int, int, int, int]


@dataclass(frozen=True)
class N45Record:
    ident: str
    center: RPoint
    r2: Fraction
    sites: frozenset[Point]
    disk_sites: frozenset[Point]
    strict_sites: int
    boundary_sites: int
    bar_count: int
    box: tuple[int, int, int, int]


def verify_n18(data: dict) -> list[N18Record]:
    records: list[N18Record] = []
    for witness in data["witnesses"]:
        ident = witness["id"]
        c2 = fpair(witness["raw_C2"])
        r2 = F(witness["raw_r2"]) / 4
        # Physical C = C2/2.  The standard grid is the physical grid shifted by
        # (+1/2,+1/2), as stated in the source certificate.
        center = (c2[0] / 2 + F(1) / 2, c2[1] / 2 + F(1) / 2)
        cells = {(int(i), int(j)) for i, j in witness["cells"]}
        if len(cells) != 18:
            raise AssertionError(f"{ident}: expected 18 distinct listed cells, got {len(cells)}")
        vertices = cells_to_vertices(cells)
        disk_vertices, box = disk_lattice_points(center, r2)
        induced_cells = induced_cells_from_vertices(disk_vertices, box)
        missing_vertices = vertices - disk_vertices
        extra_vertices = disk_vertices - vertices
        missing_cells = cells - induced_cells
        extra_cells = induced_cells - cells
        if missing_vertices or extra_vertices:
            raise AssertionError(
                f"{ident}: disk grid-vertex set mismatch; "
                f"missing={sorted(missing_vertices)}, extra={sorted(extra_vertices)}"
            )
        if missing_cells or extra_cells:
            raise AssertionError(
                f"{ident}: induced unit-cell set mismatch; "
                f"missing={sorted(missing_cells)}, extra={sorted(extra_cells)}"
            )
        strict = sum(sqdist(p, center) < r2 for p in disk_vertices)
        boundary = sum(sqdist(p, center) == r2 for p in disk_vertices)
        records.append(
            N18Record(
                ident, center, r2, frozenset(cells), frozenset(vertices),
                frozenset(disk_vertices), strict, boundary, frozenset(induced_cells), box,
            )
        )
    return records


def verify_n45(data: dict) -> list[N45Record]:
    records: list[N45Record] = []
    canonical: dict[tuple[Point, ...], str] = {}
    for witness in data["witnesses"]:
        ident = witness["id"]
        sites = {(int(x), int(y)) for x, y in witness["sites"]}
        if len(sites) != 45:
            raise AssertionError(f"{ident}: expected 45 distinct listed sites, got {len(sites)}")
        A = (F(witness["anchor_A"][0]), F(witness["anchor_A"][1]))
        B = (F(witness["anchor_B"][0]), F(witness["anchor_B"][1]))
        t = F(witness["t"])
        dx, dy = B[0] - A[0], B[1] - A[1]
        center = ((A[0] + B[0]) / 2 - t * dy, (A[1] + B[1]) / 2 + t * dx)
        r2 = sqdist(A, center)
        expected_center = fpair(witness["expected_center"])
        expected_r2 = F(witness["expected_r2"])
        if center != expected_center or r2 != expected_r2:
            raise AssertionError(
                f"{ident}: anchor/t reconstruction mismatch: "
                f"got C={center}, r2={r2}; expected C={expected_center}, r2={expected_r2}"
            )
        expected_centroid = fpair(witness["site_centroid"])
        actual_centroid = centroid(sites)
        if actual_centroid != expected_centroid:
            raise AssertionError(f"{ident}: centroid mismatch: got {actual_centroid}, expected {expected_centroid}")
        disk_sites, box = disk_lattice_points(center, r2)
        missing = sites - disk_sites
        extra = disk_sites - sites
        if missing or extra:
            raise AssertionError(f"{ident}: disk site mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
        bars = sum(((x + 1, y) in sites) + ((x, y + 1) in sites) for x, y in sites)
        code = norm_d4(sites)
        if code in canonical:
            raise AssertionError(f"{ident}: D4-equivalent to {canonical[code]}")
        canonical[code] = ident
        strict = sum(sqdist(p, center) < r2 for p in disk_sites)
        boundary = sum(sqdist(p, center) == r2 for p in disk_sites)
        records.append(
            N45Record(ident, center, r2, frozenset(sites), frozenset(disk_sites), strict, boundary, bars, box)
        )
    if len(canonical) != 12:
        raise AssertionError(f"N=45 D4 classes: expected 12, got {len(canonical)}")
    return records


def fmt(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def concise_report(n18: list[N18Record], n45: list[N45Record]) -> str:
    """Return the four user-facing checks without per-witness diagnostic noise.

    The verifier still performs the stronger exact-set equalities before this
    summary is reached.  For N=18, the upper check enumerates every integer
    lattice vertex in a certified disk box and then every unit square with all
    four vertices in the closed disk.  For N=45, it enumerates every integer
    lattice site in the certified disk box.  Any mismatch raises an AssertionError
    with the detailed witness-level information.
    """
    n18_minimum = all(r.cells <= r.induced_cells and len(r.cells) == 18 for r in n18)
    n18_maximum = all(len(r.induced_cells) <= 18 for r in n18)
    n45_minimum = all(r.sites <= r.disk_sites and len(r.sites) == 45 for r in n45)
    n45_maximum = all(len(r.disk_sites) <= 45 for r in n45)
    return "\n".join((
        f"Check at least 18 unit squares interior: {n18_minimum} ({sum(r.cells <= r.induced_cells and len(r.cells) == 18 for r in n18)}/{len(n18)})",
        f"Check no more than 18 unit squares interior: {n18_maximum} ({sum(len(r.induced_cells) <= 18 for r in n18)}/{len(n18)})",
        f"Check at least 45 lattice vertices interior: {n45_minimum} ({sum(r.sites <= r.disk_sites and len(r.sites) == 45 for r in n45)}/{len(n45)})",
        f"Check no more than 45 lattice vertices interior: {n45_maximum} ({sum(len(r.disk_sites) <= 45 for r in n45)}/{len(n45)})",
        "",
    ))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n18", type=Path, required=True)
    p.add_argument("--n45", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    print(f"Reading witness data: {args.n18}; {args.n45}")
    n18 = verify_n18(json.loads(args.n18.read_text()))
    n45 = verify_n45(json.loads(args.n45.read_text()))
    text = concise_report(n18, n45)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
