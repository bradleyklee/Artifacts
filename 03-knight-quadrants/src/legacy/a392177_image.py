#!/usr/bin/env python3
"""
Draw the red/black square-spiral knight picture for OEIS A392177/A392178.

Definition implemented:
- Square spiral cells are indexed starting at 0.
- Black and Red alternate turns.
- On each turn, the player places a knight at the smallest unoccupied spiral
  cell not attacked by an existing opposite-color knight.
- To draw the first N spiral cells, the game is simulated until both players'
  search cursors have passed N, then cells 0..N-1 are colored by final owner.

Usage:
    python3 a392177_image.py --cells 1000000 --out a392177.png
    python3 a392177_image.py --cells 4000000 --scale 1 --out a392177_4m.png

Requires Pillow for PNG output:
    python3 -m pip install pillow
"""

from __future__ import annotations

import argparse
from itertools import count
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Tuple

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "This script needs Pillow for PNG output. Install with:\n"
        "    python3 -m pip install pillow"
    ) from exc


Coord = Tuple[int, int]

KNIGHT_STEPS: Tuple[Coord, ...] = (
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1),
)


def square_spiral() -> Generator[Coord, None, None]:
    """Yield coordinates of square spiral cells 0, 1, 2, ..."""
    x, y = 0, 0
    dx, dy = 1, 0
    run_len = 1
    yield x, y

    while True:
        for _ in range(2):
            for _ in range(run_len):
                x += dx
                y += dy
                yield x, y
            dx, dy = -dy, dx
        run_len += 1


def first_spiral_coords(n: int) -> List[Coord]:
    g = square_spiral()
    return [next(g) for _ in range(n)]


def generate_owners(n_cells: int) -> Dict[Coord, int]:
    """
    Return {coord: color}, with color 0 = black, 1 = red, for the final
    ownership of the first n_cells spiral cells.
    """
    owned = [set(), set()]          # owned[0] black, owned[1] red
    spirals = [square_spiral(), square_spiral()]
    cursor = [-1, -1]              # last spiral index examined by each color

    while cursor[0] < n_cells or cursor[1] < n_cells:
        for turn in (0, 1):
            other = 1 - turn
            for k in count(cursor[turn] + 1):
                loc = next(spirals[turn])
                cursor[turn] = k

                if loc in owned[other]:
                    continue

                if all((loc[0] + dx, loc[1] + dy) not in owned[other]
                       for dx, dy in KNIGHT_STEPS):
                    owned[turn].add(loc)
                    break

    owners: Dict[Coord, int] = {}
    for color in (0, 1):
        for loc in owned[color]:
            owners[loc] = color
    return owners


def draw(n_cells: int, out_path: Path, scale: int, empty: str) -> None:
    coords = first_spiral_coords(n_cells)
    owners = generate_owners(n_cells)

    min_x = min(x for x, _ in coords)
    max_x = max(x for x, _ in coords)
    min_y = min(y for _, y in coords)
    max_y = max(y for _, y in coords)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    empty_colors = {
        "white": (255, 255, 255),
        "gray": (160, 160, 160),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
    }
    img = Image.new("RGB", (width, height), empty_colors[empty])
    pix = img.load()

    for x, y in coords:
        owner = owners.get((x, y))
        if owner == 0:
            color = (0, 0, 0)
        elif owner == 1:
            color = (255, 0, 0)
        else:
            continue

        # Image y-axis points downward; spiral y-axis points upward.
        pix[x - min_x, max_y - y] = color

    if scale != 1:
        img = img.resize((width * scale, height * scale), Image.Resampling.NEAREST)

    img.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cells", type=int, default=1_000_000,
        help="number of spiral cells to render; OEIS image link uses 1,000,000"
    )
    parser.add_argument("--out", type=Path, default=Path("a392177.png"))
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument(
        "--empty", choices=("white", "gray", "black", "red"), default="white",
        help="color for cells among 0..cells-1 that are not occupied"
    )
    args = parser.parse_args()

    if args.cells <= 0:
        raise SystemExit("--cells must be positive")
    if args.scale <= 0:
        raise SystemExit("--scale must be positive")

    draw(args.cells, args.out, args.scale, args.empty)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
