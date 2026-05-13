#!/usr/bin/env python3
"""
Generate red/black greedy-knight images on Z^2.

Two orderings are supported:

1) spiral
   The original square-spiral order.

2) rings
   Concentric-ring order:
     (a) increasing squared distance x^2 + y^2
     (b) increasing angle atan2(y, x), mapped into [0, 2*pi),
         i.e. CCW starting from the positive x-axis.

For rings, a "safe depiction" mode is also supported:

    outer square  ⊃  circle  ⊃  inner square

- The ordered game is played on all lattice points in the outer square.
- We simulate until both players have scanned past the last point in the circle.
- We then render only the inner square.

This is meant to reduce edge artifacts / false positives in the rendered image.

Examples
--------
Original spiral picture:
    python3 a392177_image_safe.py --order spiral --cells 1000000 --out spiral.png

Plain rings picture (render first N ordered lattice points):
    python3 a392177_image_safe.py --order rings --cells 200000 --out rings.png

Safe rings picture:
    python3 a392177_image_safe.py --order rings --safe-inner-square \\
        --inner-half 500 --out rings_safe.png
"""

from __future__ import annotations

import argparse
import math
from itertools import count
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "This script needs Pillow. Install it with:\n"
        "    python3 -m pip install pillow"
    ) from exc


KNIGHT = (
    ( 1,  2), ( 2,  1), (-1,  2), (-2,  1),
    ( 1, -2), ( 2, -1), (-1, -2), (-2, -1),
)


def spiral():
    """Infinite square-spiral order on Z^2, starting at (0, 0)."""
    x = y = 0
    yield x, y
    step = 1
    while True:
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            for _ in range(step):
                x += dx
                y += dy
                yield x, y
            if dx == 0:
                step += 1


def angle_ccw_from_pos_x(x: int, y: int) -> float:
    """Angle in [0, 2*pi), CCW from the positive x-axis."""
    a = math.atan2(y, x)
    if a < 0:
        a += 2.0 * math.pi
    return a


def ring_order_square_points(half: int):
    """
    All lattice points in the square [-half, half]^2, ordered by:
      1) x^2 + y^2
      2) angle CCW from +x
      3) x, y (harmless deterministic tie-break)
    """
    pts = [(x, y) for y in range(-half, half + 1) for x in range(-half, half + 1)]
    pts.sort(key=lambda p: (
        p[0] * p[0] + p[1] * p[1],
        angle_ccw_from_pos_x(p[0], p[1]),
        p[0],
        p[1],
    ))
    return pts


def attacked_by_enemy(cell, enemy):
    x, y = cell
    for dx, dy in KNIGHT:
        if (x + dx, y + dy) in enemy:
            return True
    return False


def generate_from_finite_order(points, trusted_last_index: int):
    """
    Greedy two-color game on a finite ordered list of lattice points.

    Each player has its own scan cursor into the same ordered list.
    On a turn, the player takes the first point at/after its cursor that is:
      - not already occupied by the opposite color
      - not attacked by an opposite-color knight

    We stop once both scan cursors have passed trusted_last_index.

    Returns: black_set, red_set
    """
    black = set()
    red = set()
    cursor = [-1, -1]

    while cursor[0] <= trusted_last_index or cursor[1] <= trusted_last_index:
        for color in (0, 1):
            mine = black if color == 0 else red
            enemy = red if color == 0 else black

            placed = False
            start = cursor[color] + 1
            for i in range(start, len(points)):
                cell = points[i]
                cursor[color] = i
                if cell in enemy:
                    continue
                if attacked_by_enemy(cell, enemy):
                    continue
                mine.add(cell)
                placed = True
                break

            if not placed:
                cursor[color] = len(points)

    return black, red


def generate_spiral(n: int):
    """Original infinite-square-spiral version: determine ownership on first n cells."""
    black = set()
    red = set()
    streams = [spiral(), spiral()]
    cursor = [-1, -1]

    while cursor[0] < n or cursor[1] < n:
        for color in (0, 1):
            mine = black if color == 0 else red
            enemy = red if color == 0 else black

            for i in count(cursor[color] + 1):
                cell = next(streams[color])
                cursor[color] = i
                if cell in enemy:
                    continue
                if attacked_by_enemy(cell, enemy):
                    continue
                mine.add(cell)
                break

    return black, red


def first_n_spiral_cells(n: int):
    s = spiral()
    return [next(s) for _ in range(n)]


def safe_rings_geometry(inner_half: int, circle_radius: int | None, outer_half: int | None):
    """
    Geometry:
      inner square  ⊂  circle  ⊂  outer square

    Defaults:
      circle_radius = ceil(inner_half * sqrt(2))
      outer_half    = circle_radius
    """
    if inner_half < 0:
        raise ValueError("inner_half must be nonnegative")

    if circle_radius is None:
        circle_radius = math.ceil(inner_half * math.sqrt(2.0))
    if outer_half is None:
        outer_half = circle_radius

    if circle_radius < math.ceil(inner_half * math.sqrt(2.0)):
        raise ValueError("circle_radius is too small to contain the inner square")
    if outer_half < circle_radius:
        raise ValueError("outer_half must be at least circle_radius")

    return circle_radius, outer_half


def draw_spiral(n: int, out_path: Path, scale: int, bg_rgb):
    black, red = generate_spiral(n)
    cells = first_n_spiral_cells(n)

    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    w = max_x - min_x + 1
    h = max_y - min_y + 1

    img = Image.new("RGB", (w, h), bg_rgb)
    pix = img.load()

    for x, y in cells:
        px = x - min_x
        py = max_y - y
        if (x, y) in black:
            pix[px, py] = (0, 0, 0)
        elif (x, y) in red:
            pix[px, py] = (255, 0, 0)

    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)

    img.save(out_path)


def draw_plain_rings(n: int, out_path: Path, scale: int, bg_rgb):
    """
    Render the first n points in ring order.
    We choose the smallest square centered at the origin containing at least n lattice points,
    then order all points in that square and take the first n.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    half = math.ceil((math.sqrt(n) - 1.0) / 2.0)
    points = ring_order_square_points(half)
    cells = points[:n]
    black, red = generate_from_finite_order(points, n - 1)

    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    w = max_x - min_x + 1
    h = max_y - min_y + 1

    img = Image.new("RGB", (w, h), bg_rgb)
    pix = img.load()

    visible = set(cells)
    for x, y in visible:
        px = x - min_x
        py = max_y - y
        if (x, y) in black:
            pix[px, py] = (0, 0, 0)
        elif (x, y) in red:
            pix[px, py] = (255, 0, 0)

    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)

    img.save(out_path)


def draw_safe_rings(inner_half: int, out_path: Path, scale: int, bg_rgb,
                    circle_radius: int | None = None, outer_half: int | None = None):
    circle_radius, outer_half = safe_rings_geometry(inner_half, circle_radius, outer_half)

    points = ring_order_square_points(outer_half)

    circle_r2 = circle_radius * circle_radius
    trusted_indices = [
        i for i, (x, y) in enumerate(points)
        if x * x + y * y <= circle_r2
    ]
    trusted_last_index = max(trusted_indices) if trusted_indices else -1

    black, red = generate_from_finite_order(points, trusted_last_index)

    w = 2 * inner_half + 1
    h = 2 * inner_half + 1
    img = Image.new("RGB", (w, h), bg_rgb)
    pix = img.load()

    for y in range(-inner_half, inner_half + 1):
        for x in range(-inner_half, inner_half + 1):
            px = x + inner_half
            py = inner_half - y
            if (x, y) in black:
                pix[px, py] = (0, 0, 0)
            elif (x, y) in red:
                pix[px, py] = (255, 0, 0)

    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)

    img.save(out_path)


def parse_bg(name: str):
    table = {
        "white": (255, 255, 255),
        "gray": (160, 160, 160),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
    }
    return table[name]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", choices=["spiral", "rings"], default="spiral")
    ap.add_argument("--cells", type=int, default=100000,
                    help="Used by spiral and plain rings modes")
    ap.add_argument("--safe-inner-square", action="store_true",
                    help="For rings mode: render inner square from square⊃circle⊃square pipeline")
    ap.add_argument("--inner-half", type=int, default=500,
                    help="For safe rings: render the square [-inner_half, inner_half]^2")
    ap.add_argument("--circle-radius", type=int, default=None,
                    help="For safe rings: trusted circular radius (default ceil(inner_half*sqrt(2)))")
    ap.add_argument("--outer-half", type=int, default=None,
                    help="For safe rings: outer square half-side (default circle_radius)")
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--bg", choices=["white", "gray", "black", "red"], default="white")
    ap.add_argument("--out", type=Path, default=Path("out.png"))
    args = ap.parse_args()

    if args.scale <= 0:
        raise SystemExit("--scale must be positive")

    bg_rgb = parse_bg(args.bg)

    if args.order == "spiral":
        draw_spiral(args.cells, args.out, args.scale, bg_rgb)
    else:
        if args.safe_inner_square:
            draw_safe_rings(
                inner_half=args.inner_half,
                out_path=args.out,
                scale=args.scale,
                bg_rgb=bg_rgb,
                circle_radius=args.circle_radius,
                outer_half=args.outer_half,
            )
        else:
            draw_plain_rings(args.cells, args.out, args.scale, bg_rgb)

    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
