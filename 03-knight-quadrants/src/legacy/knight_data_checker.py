#!/usr/bin/env python3
"""
Data checker for the greedy knight covering game on Z^2.

Rule-set checked:
- There is a fixed sequencing of lattice squares.
- Colors take turns cyclically.
- A square may be covered at most once total.
- A color may cover the first sequentially available square that:
    (1) is unoccupied
    (2) is not knight-attacked by any other color

This script can:
- generate safe-ring ordered data,
- generate the move list,
- independently verify every move,
- write a CSV move log for inspection.

Examples:
    python3 knight_data_checker.py --colors rb --inner-half 20 --check
    python3 knight_data_checker.py --colors rgb --inner-half 50 --check --csv rgb_moves.csv
    python3 knight_data_checker.py --colors rgby --inner-half 50 --check --limit-moves 200
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

Coord = Tuple[int, int]

KNIGHT: Tuple[Coord, ...] = (
    ( 1,  2), ( 2,  1), (-1,  2), (-2,  1),
    ( 1, -2), ( 2, -1), (-1, -2), (-2, -1),
)

COLOR_NAMES = {
    "r": "red",
    "b": "black",
    "g": "green",
    "y": "yellow",
}


def angle_ccw_from_pos_x(x: int, y: int) -> float:
    a = math.atan2(y, x)
    if a < 0:
        a += 2.0 * math.pi
    return a


def ring_order_square_points(half: int) -> List[Coord]:
    pts = [(x, y) for y in range(-half, half + 1)
                  for x in range(-half, half + 1)]
    pts.sort(key=lambda p: (
        p[0] * p[0] + p[1] * p[1],
        angle_ccw_from_pos_x(p[0], p[1]),
        p[0],
        p[1],
    ))
    return pts


def safe_ring_order(inner_half: int) -> Tuple[List[Coord], int, int, int]:
    """
    Return:
      points, trusted_last_index, circle_radius, outer_half

    Geometry:
      outer square contains trusted circle contains rendered inner square.
    """
    if inner_half < 0:
        raise ValueError("inner_half must be nonnegative")

    circle_radius = math.ceil(inner_half * math.sqrt(2.0))
    outer_half = circle_radius
    points = ring_order_square_points(outer_half)

    circle_r2 = circle_radius * circle_radius
    trusted = [
        i for i, (x, y) in enumerate(points)
        if x * x + y * y <= circle_r2
    ]
    if not trusted:
        raise RuntimeError("empty trusted circle")

    return points, max(trusted), circle_radius, outer_half


def is_attacked_by_other_colors(
    cell: Coord,
    color: int,
    owned: Sequence[Set[Coord]],
) -> bool:
    x, y = cell
    for dx, dy in KNIGHT:
        q = (x + dx, y + dy)
        for c, pieces in enumerate(owned):
            if c != color and q in pieces:
                return True
    return False


def legal_for_color(
    cell: Coord,
    color: int,
    owned: Sequence[Set[Coord]],
    occupied: Set[Coord],
) -> bool:
    if cell in occupied:
        return False
    if is_attacked_by_other_colors(cell, color, owned):
        return False
    return True


def generate_moves(
    points: Sequence[Coord],
    trusted_last_index: int,
    colors: str,
    limit_moves: int | None = None,
) -> List[Dict[str, object]]:
    ncolors = len(colors)
    owned: List[Set[Coord]] = [set() for _ in range(ncolors)]
    occupied: Set[Coord] = set()
    cursor = [-1] * ncolors
    moves: List[Dict[str, object]] = []

    while any(c <= trusted_last_index for c in cursor):
        for color in range(ncolors):
            placed = False
            start_index = cursor[color] + 1

            for i in range(start_index, len(points)):
                cell = points[i]
                cursor[color] = i

                if not legal_for_color(cell, color, owned, occupied):
                    continue

                owned[color].add(cell)
                occupied.add(cell)
                moves.append({
                    "move": len(moves) + 1,
                    "color_index": color,
                    "color": colors[color],
                    "color_name": COLOR_NAMES.get(colors[color], colors[color]),
                    "order_index": i,
                    "x": cell[0],
                    "y": cell[1],
                    "start_index": start_index,
                    "cursor_after": i,
                })
                placed = True
                break

            if not placed:
                cursor[color] = len(points)
                moves.append({
                    "move": len(moves) + 1,
                    "color_index": color,
                    "color": colors[color],
                    "color_name": COLOR_NAMES.get(colors[color], colors[color]),
                    "order_index": None,
                    "x": None,
                    "y": None,
                    "start_index": start_index,
                    "cursor_after": len(points),
                    "pass": True,
                })

            if limit_moves is not None and len(moves) >= limit_moves:
                return moves

    return moves


def verify_moves(
    points: Sequence[Coord],
    trusted_last_index: int,
    colors: str,
    moves: Sequence[Dict[str, object]],
    verbose: bool = False,
) -> bool:
    ncolors = len(colors)
    owned: List[Set[Coord]] = [set() for _ in range(ncolors)]
    occupied: Set[Coord] = set()
    cursor = [-1] * ncolors

    ok = True

    for m in moves:
        move_no = int(m["move"])
        color = int(m["color_index"])
        expected_color = (move_no - 1) % ncolors

        if color != expected_color:
            print(
                f"FAIL move {move_no}: expected color index "
                f"{expected_color}, got {color}"
            )
            ok = False
            break

        start = cursor[color] + 1
        claimed_index = m.get("order_index")

        if claimed_index is None:
            # Pass is valid only if there is no legal cell from start onward.
            for i in range(start, len(points)):
                if legal_for_color(points[i], color, owned, occupied):
                    print(
                        f"FAIL move {move_no}: pass, but earlier legal cell "
                        f"exists at index {i}, coord {points[i]}"
                    )
                    ok = False
                    break
            cursor[color] = len(points)
            if not ok:
                break
            continue

        i = int(claimed_index)
        cell = (int(m["x"]), int(m["y"]))

        if i < start:
            print(
                f"FAIL move {move_no}: order index {i} is before "
                f"cursor start {start}"
            )
            ok = False
            break

        if i >= len(points):
            print(f"FAIL move {move_no}: order index {i} out of range")
            ok = False
            break

        if points[i] != cell:
            print(
                f"FAIL move {move_no}: index {i} is {points[i]}, "
                f"but move claims {cell}"
            )
            ok = False
            break

        # Minimality check: every earlier candidate from this color's cursor
        # must be illegal in the current pre-move state.
        for j in range(start, i):
            if legal_for_color(points[j], color, owned, occupied):
                print(
                    f"FAIL move {move_no}: non-minimal choice. "
                    f"Earlier legal index {j}, coord {points[j]}, "
                    f"chosen index {i}, coord {cell}"
                )
                ok = False
                break
        if not ok:
            break

        # Legality check for chosen square.
        if not legal_for_color(cell, color, owned, occupied):
            reasons = []
            if cell in occupied:
                reasons.append("already occupied")
            if is_attacked_by_other_colors(cell, color, owned):
                reasons.append("attacked by other color")
            print(
                f"FAIL move {move_no}: chosen cell {cell} illegal: "
                + ", ".join(reasons)
            )
            ok = False
            break

        owned[color].add(cell)
        occupied.add(cell)
        cursor[color] = i

        if verbose and move_no <= 20:
            print(
                f"ok move {move_no}: {colors[color]} "
                f"index={i} coord={cell}"
            )

    if ok:
        print(
            f"PASS: verified {len(moves)} moves, "
            f"{len(occupied)} occupied cells, {len(colors)} colors"
        )

    return ok


def write_csv(path: Path, moves: Sequence[Dict[str, object]]) -> None:
    fields = [
        "move", "color_index", "color", "color_name",
        "order_index", "x", "y", "start_index", "cursor_after",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m in moves:
            w.writerow({k: m.get(k, "") for k in fields})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--colors", default="rb",
                    help="Color cycle, e.g. rb, rgb, rgby")
    ap.add_argument("--inner-half", type=int, default=50)
    ap.add_argument("--limit-moves", type=int, default=None)
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if len(set(args.colors)) != len(args.colors):
        raise SystemExit("--colors must not repeat color letters")
    if len(args.colors) < 2:
        raise SystemExit("--colors must contain at least two colors")

    points, trusted_last_index, circle_radius, outer_half = safe_ring_order(
        args.inner_half
    )

    print(
        f"safe rings: inner_half={args.inner_half}, "
        f"circle_radius={circle_radius}, outer_half={outer_half}, "
        f"points={len(points)}, trusted_last_index={trusted_last_index}, "
        f"colors={args.colors}"
    )

    moves = generate_moves(
        points,
        trusted_last_index,
        args.colors,
        limit_moves=args.limit_moves,
    )

    print(f"generated moves: {len(moves)}")

    if args.csv is not None:
        write_csv(args.csv, moves)
        print(f"wrote {args.csv}")

    if args.check:
        ok = verify_moves(
            points,
            trusted_last_index,
            args.colors,
            moves,
            verbose=args.verbose,
        )
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
