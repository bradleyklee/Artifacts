#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, math
from PIL import Image

KNIGHT = (
    (1,2),(2,1),(-1,2),(-2,1),
    (1,-2),(2,-1),(-1,-2),(-2,-1),
)

BLACK = (0,0,0)
RED = (255,0,0)
WHITE = (255,255,255)

def angle_ccw_from_pos_x(x:int, y:int) -> float:
    a = math.atan2(y, x)
    if a < 0:
        a += 2.0 * math.pi
    return a

def ring_order_square_points(half:int):
    pts = [(x,y) for y in range(-half, half+1) for x in range(-half, half+1)]
    pts.sort(key=lambda p: (p[0]*p[0] + p[1]*p[1], angle_ccw_from_pos_x(p[0], p[1]), p[0], p[1]))
    return pts

def attacked_by_enemy(cell, enemy):
    x, y = cell
    for dx, dy in KNIGHT:
        if (x+dx, y+dy) in enemy:
            return True
    return False

def generate_two_color(points, trusted_last_index:int):
    owned = [set(), set()]   # 0 black, 1 red
    occupied = set()
    cursor = [-1, -1]

    while any(c <= trusted_last_index for c in cursor):
        for color in (0,1):
            enemy = owned[1-color]
            placed = False
            for i in range(cursor[color]+1, len(points)):
                cell = points[i]
                cursor[color] = i
                if cell in occupied:
                    continue
                if attacked_by_enemy(cell, enemy):
                    continue
                owned[color].add(cell)
                occupied.add(cell)
                placed = True
                break
            if not placed:
                cursor[color] = len(points)
    return owned

def draw_safe(inner_half:int, out_path:Path):
    circle_radius = math.ceil(inner_half * math.sqrt(2.0))
    outer_half = circle_radius
    points = ring_order_square_points(outer_half)
    circle_r2 = circle_radius * circle_radius
    trusted_last_index = max(i for i,(x,y) in enumerate(points) if x*x + y*y <= circle_r2)
    black, red = generate_two_color(points, trusted_last_index)

    w = h = 2*inner_half + 1
    img = Image.new('RGB', (w,h), WHITE)
    pix = img.load()
    for x,y in black:
        if -inner_half <= x <= inner_half and -inner_half <= y <= inner_half:
            pix[x + inner_half, inner_half - y] = BLACK
    for x,y in red:
        if -inner_half <= x <= inner_half and -inner_half <= y <= inner_half:
            pix[x + inner_half, inner_half - y] = RED
    img.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inner-half', type=int, default=500)
    ap.add_argument('--out', type=Path, default=Path('rings_safe_rb_1001_corrected.png'))
    args = ap.parse_args()
    draw_safe(args.inner_half, args.out)
    print(f'wrote {args.out}')

if __name__ == '__main__':
    main()
