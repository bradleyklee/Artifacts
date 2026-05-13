#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, math
from PIL import Image

KNIGHT = (
    ( 1,  2), ( 2,  1), (-1,  2), (-2,  1),
    ( 1, -2), ( 2, -1), (-1, -2), (-2, -1),
)

COLORS = (
    (255, 0, 0),   # red
    (0, 180, 0),   # green
    (0, 0, 255),   # blue
)

def angle_ccw_from_pos_x(x: int, y: int) -> float:
    a = math.atan2(y, x)
    if a < 0:
        a += 2.0 * math.pi
    return a

def ring_order_square_points(half: int):
    pts = [(x, y) for y in range(-half, half + 1) for x in range(-half, half + 1)]
    pts.sort(key=lambda p: (
        p[0] * p[0] + p[1] * p[1],
        angle_ccw_from_pos_x(p[0], p[1]),
        p[0],
        p[1],
    ))
    return pts

def attacked_by_other_colors(cell, color, owned):
    x, y = cell
    for dx, dy in KNIGHT:
        p = (x + dx, y + dy)
        for c in range(3):
            if c != color and p in owned[c]:
                return True
    return False

def generate_three_color(points, trusted_last_index: int):
    owned = [set(), set(), set()]
    occupied = set()
    cursor = [-1, -1, -1]

    while any(c <= trusted_last_index for c in cursor):
        for color in (0, 1, 2):
            placed = False
            for i in range(cursor[color] + 1, len(points)):
                cell = points[i]
                cursor[color] = i
                if cell in occupied:
                    continue
                if attacked_by_other_colors(cell, color, owned):
                    continue
                owned[color].add(cell)
                occupied.add(cell)
                placed = True
                break
            if not placed:
                cursor[color] = len(points)
    return owned

def draw_safe_rgb(inner_half: int, out_path: Path):
    circle_radius = math.ceil(inner_half * math.sqrt(2.0))
    outer_half = circle_radius

    points = ring_order_square_points(outer_half)
    circle_r2 = circle_radius * circle_radius
    trusted_last_index = max(
        i for i, (x, y) in enumerate(points)
        if x * x + y * y <= circle_r2
    )

    owned = generate_three_color(points, trusted_last_index)

    w = 2 * inner_half + 1
    h = 2 * inner_half + 1
    img = Image.new("RGB", (w, h), (255, 255, 255))
    pix = img.load()

    for color in range(3):
        rgb = COLORS[color]
        for x, y in owned[color]:
            if -inner_half <= x <= inner_half and -inner_half <= y <= inner_half:
                px = x + inner_half
                py = inner_half - y
                pix[px, py] = rgb

    img.save(out_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inner-half", type=int, default=500)
    ap.add_argument("--out", type=Path, default=Path("rings_safe_rgb.png"))
    args = ap.parse_args()
    draw_safe_rgb(args.inner_half, args.out)
    print(f"wrote {args.out}")

if __name__ == "__main__":
    main()
