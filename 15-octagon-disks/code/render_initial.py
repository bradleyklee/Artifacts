#!/usr/bin/env python3
"""Render exact octagon initial states as clean SVGs.

Inputs supported:
  data/three-body/initials/class_*.initial.json
  data/clock/initials/mask_*.json

The renderer reads positions, velocities and container size from its input. It
uses one shared 4.8.8 geometry routine, has no handwritten per-image layout,
and emits diagrams with no visible text: container, tiling, moving octagons,
and literal black velocity arrows only.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

SQRT2 = math.sqrt(2.0)
EDGE = 1.0
STEP = 2.0 + SQRT2
RADIUS = EDGE / (2.0 * math.sin(math.pi / 8.0))

COLORS = {
    "P0": "#e67e22", "P1": "#18a999", "P2": "#7d72cf",
    "I0": "#e67e22", "I1": "#18a999", "I2": "#7d72cf", "I3": "#d85878",
    "O0": "#3a78be", "O1": "#b8862e", "O2": "#9d63b5", "O3": "#3c9d86",
}
FALLBACK = ["#e67e22", "#18a999", "#7d72cf", "#d85878", "#3a78be", "#b8862e"]


def qsqrt2(value: Any) -> float:
    if isinstance(value, dict):
        return float(Fraction(value["a"]) + Fraction(value["b"]) * SQRT2)
    return float(Fraction(value))


def parse_side(text: str) -> float:
    """Parse compact exact side form a+b*sqrt(2), used by three-body initials."""
    clean = text.replace(" ", "")
    match = re.fullmatch(r"([+-]?[^+\-]+)([+\-].+)\*sqrt\(2\)", clean)
    if not match:
        raise ValueError(f"unsupported exact container_side: {text!r}")
    return float(Fraction(match.group(1))) + float(Fraction(match.group(2))) * SQRT2


def polygon_points(points: Iterable[tuple[float, float]]) -> str:
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)


def octagon_relative() -> list[tuple[float, float]]:
    return [
        (RADIUS * math.cos(math.pi / 8.0 + k * math.pi / 4.0),
         RADIUS * math.sin(math.pi / 8.0 + k * math.pi / 4.0))
        for k in range(8)
    ]


def normalize_input(obj: dict[str, Any]) -> tuple[str, str, float, list[tuple[str, float, float, float, float]]]:
    # Full three-body certificate.
    if "instance" in obj and "model" in obj:
        ins = obj["instance"]
        bodies = [
            (str(b["id"]), qsqrt2(b["position"]["x"]), qsqrt2(b["position"]["y"]),
             qsqrt2(b["velocity"]["vx"]), qsqrt2(b["velocity"]["vy"]))
            for b in ins["initial_state"]
        ]
        return "three-body", f"class_{ins.get('class', 'unknown')}", qsqrt2(ins["container_half_box"]), bodies

    # Compact three-body initial.
    if "container_side" in obj and "initial" in obj:
        bodies = []
        for i, b in enumerate(obj["initial"]):
            bodies.append((
                f"P{i}", qsqrt2(b["position"]["x"]), qsqrt2(b["position"]["y"]),
                qsqrt2(b["velocity"]["x"]), qsqrt2(b["velocity"]["y"]),
            ))
        return "three-body", f"class_{obj.get('class', 'unknown')}", parse_side(obj["container_side"]) / 2.0, bodies

    # Clock C4 seed.
    if obj.get("schema") == "c4-clock-mask-seed/v1":
        bodies = [
            (str(b["id"]), qsqrt2(b["position"]["x"]), qsqrt2(b["position"]["y"]),
             qsqrt2(b["velocity"]["vx"]), qsqrt2(b["velocity"]["vy"]))
            for b in obj["state"]
        ]
        return "clock", f"mask_{int(obj['mask_bits']):03d}", qsqrt2(obj["container"]["half_box"]), bodies

    raise ValueError("unsupported initial/certificate schema")


def explicit_arrow(cx: float, cy: float, vx: float, vy: float, scale: float) -> str:
    """Centered shaft plus triangle whose base covers the shaft endpoint."""
    norm = math.hypot(vx, vy)
    if norm == 0:
        return ""
    ux, uy = vx / norm, -vy / norm  # SVG y-axis is inverted.
    half_shaft = 0.28 * scale
    head_len = 0.20 * scale
    head_half_width = 0.105 * scale
    x0, y0 = cx - half_shaft * ux, cy - half_shaft * uy
    xb, yb = cx + half_shaft * ux, cy + half_shaft * uy
    xt, yt = xb + head_len * ux, yb + head_len * uy
    px, py = -uy, ux
    xl, yl = xb + head_half_width * px, yb + head_half_width * py
    xr, yr = xb - head_half_width * px, yb - head_half_width * py
    return (
        f'<line x1="{x0:.3f}" y1="{y0:.3f}" x2="{xb:.3f}" y2="{yb:.3f}" '
        'stroke="#111111" stroke-width="3.25" stroke-linecap="round"/>'
        f'<polygon points="{xt:.3f},{yt:.3f} {xl:.3f},{yl:.3f} {xr:.3f},{yr:.3f}" fill="#111111"/>'
    )


def render_svg(obj: dict[str, Any]) -> str:
    family, name, half, bodies = normalize_input(obj)
    width = height = 960
    margin = 54
    panel = width - 2 * margin
    scale = panel / (2 * half)
    oct_rel = octagon_relative()

    def xy(x: float, y: float) -> tuple[float, float]:
        return margin + (x + half) * scale, margin + (half - y) * scale

    parts: list[str] = []
    add = parts.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<svg xmlns="http://www.w3.org/2000/svg" width="960" height="960" viewBox="0 0 960 960" role="img">')
    add(f'<title>{family} {name}: initial condition</title>')
    add('<desc>Code-generated from exact source data: unit-edge 4.8.8 tiling, moving octagons, and literal black velocity arrows.</desc>')
    add('<rect width="960" height="960" fill="#ffffff"/>')
    add(f'<defs><clipPath id="arena"><rect x="{margin}" y="{margin}" width="{panel}" height="{panel}"/></clipPath></defs>')
    add(f'<rect x="{margin}" y="{margin}" width="{panel}" height="{panel}" fill="#fcfcfd" stroke="#111827" stroke-width="2.6"/>')
    add('<g clip-path="url(#arena)">')

    # The unit 4.8.8 tiling consists of two interleaved octagon-center lattices;
    # unit squares sit between horizontal/vertical same-sublattice neighbors.
    n = int(math.ceil((half + STEP) / STEP)) + 2
    squares: set[tuple[float, float]] = set()
    octagons: list[tuple[float, float]] = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            for ox, oy in ((0.0, 0.0), (STEP / 2.0, STEP / 2.0)):
                cx, cy = i * STEP + ox, j * STEP + oy
                octagons.append((cx, cy))
                squares.add((round(cx + STEP / 2.0, 12), round(cy, 12)))
                squares.add((round(cx, 12), round(cy + STEP / 2.0, 12)))

    for cx, cy in sorted(squares):
        x0, y0 = xy(cx - 0.5, cy - 0.5)
        x1, y1 = xy(cx + 0.5, cy + 0.5)
        add(f'<rect x="{min(x0,x1):.3f}" y="{min(y0,y1):.3f}" width="{abs(x1-x0):.3f}" height="{abs(y1-y0):.3f}" fill="#ffffff" stroke="#d9dee5" stroke-width="0.70"/>')
    for cx, cy in octagons:
        pts = [xy(cx + dx, cy + dy) for dx, dy in oct_rel]
        add(f'<polygon points="{polygon_points(pts)}" fill="#f6f7f9" stroke="#cfd5dd" stroke-width="0.85"/>')

    for index, (body_id, x, y, vx, vy) in enumerate(bodies):
        color = COLORS.get(body_id, FALLBACK[index % len(FALLBACK)])
        pts = [xy(x + dx, y + dy) for dx, dy in oct_rel]
        add(f'<polygon points="{polygon_points(pts)}" fill="{color}" stroke="#2b2b2b" stroke-width="2.0"/>')
        cx, cy = xy(x, y)
        add(explicit_arrow(cx, cy, vx, vy, scale))

    add('</g>')
    add(f'<rect x="{margin}" y="{margin}" width="{panel}" height="{panel}" fill="none" stroke="#111827" stroke-width="2.6"/>')
    add('</svg>')
    return "\n".join(parts) + "\n"


def render_one(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_svg(json.loads(input_path.read_text())), encoding="utf-8")


def render_all(root: Path) -> None:
    for source in sorted((root / "data" / "three-body" / "initial").glob("*.json")):
        stem = source.stem
        render_one(source, root / "data" / "three-body" / "images" / f"{stem}.svg")
    for source in sorted((root / "data" / "clock" / "initial").glob("*.json")):
        stem = source.stem
        render_one(source, root / "data" / "clock" / "images" / f"{stem}.svg")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--all", type=Path)
    args = parser.parse_args()
    if args.all:
        if args.input or args.out:
            parser.error("--all cannot be combined with input/--out")
        render_all(args.all)
    elif args.input and args.out:
        render_one(args.input, args.out)
    else:
        parser.error("use INPUT --out OUTPUT or --all ROOT")

if __name__ == "__main__":
    main()
