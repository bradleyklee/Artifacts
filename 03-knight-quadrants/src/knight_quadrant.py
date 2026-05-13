#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

Coord = Tuple[int, int]
HEX_DIRS: Tuple[Coord, ...] = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
SQUARE_KNIGHT: Tuple[Coord, ...] = (
    (1, 2), (2, 1), (-1, 2), (-2, 1),
    (1, -2), (2, -1), (-1, -2), (-2, -1),
)
CSV_FIELDS = ['move', 'color_index', 'color', 'order_index', 'a', 'b', 'cursor_start', 'cursor_after']
POINT_FIELDS = ['order_index', 'a', 'b']
COLOR_RGB = {'r': (255, 0, 0), 'b': (0, 0, 0), 'g': (0, 180, 0), 'y': (220, 180, 0)}
COLOR_STROKE = {'r': '#d11c24', 'b': '#000000', 'g': '#138a13', 'y': '#c8a000'}


@dataclass(frozen=True)
class Metadata:
    artifact_index: str
    artifact_name: str
    kind: str
    geometry: str
    attack: str
    order: str
    colors: str
    radius: int
    trusted_radius: int
    outer_radius: int
    visible_shape: str
    trusted_last_index: int


def add(a: Coord, b: Coord) -> Coord:
    return (a[0] + b[0], a[1] + b[1])


def mul(a: Coord, k: int) -> Coord:
    return (a[0] * k, a[1] * k)


def is_neighbor_hex(a: Coord, b: Coord) -> bool:
    d = (b[0] - a[0], b[1] - a[1])
    return d in HEX_DIRS


def projected_xy(p: Coord) -> Tuple[float, float]:
    a, b = p
    return (a + 0.5 * b, (math.sqrt(3.0) / 2.0) * b)


def angle01(x: float, y: float) -> float:
    t = math.atan2(y, x)
    return t if t >= 0 else t + 2.0 * math.pi


def square_key(p: Coord) -> Tuple[float, float, int, int]:
    a, b = p
    return (a * a + b * b, angle01(a, b), a, b)


def hex_distatan_key(p: Coord) -> Tuple[int, float, int, int]:
    a, b = p
    x, y = projected_xy(p)
    return (a * a + a * b + b * b, angle01(x, y), a, b)


def axial_distance(p: Coord) -> int:
    a, b = p
    c = -a - b
    return max(abs(a), abs(b), abs(c))


def square_spiral_points(half: int) -> List[Coord]:
    needed = (2 * half + 1) * (2 * half + 1)
    out: List[Coord] = [(0, 0)]
    x = y = 0
    step = 1
    while len(out) < needed:
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            for _ in range(step):
                x += dx
                y += dy
                if -half <= x <= half and -half <= y <= half:
                    out.append((x, y))
                    if len(out) >= needed:
                        return out
            if dx == 0:
                step += 1
    return out


def hex_ball(radius: int) -> List[Coord]:
    return [
        (a, b)
        for a in range(-radius, radius + 1)
        for b in range(-radius, radius + 1)
        if axial_distance((a, b)) <= radius
    ]


def hex_ring_angle_sorted(k: int) -> List[Coord]:
    pts = [
        (a, b)
        for a in range(-k, k + 1)
        for b in range(-k, k + 1)
        if axial_distance((a, b)) == k
    ]
    pts.sort(key=hex_distatan_key)
    return pts


def hex_ring_cycle(k: int) -> List[Coord]:
    if k <= 0:
        return []
    p = mul(HEX_DIRS[4], k)
    out: List[Coord] = []
    for d in HEX_DIRS:
        for _ in range(k):
            out.append(p)
            p = add(p, d)
    return out


def rotate(lst: List[Coord], idx: int) -> List[Coord]:
    return lst[idx:] + lst[:idx]


def hex_spiral_points(radius: int) -> List[Coord]:
    out: List[Coord] = [(0, 0)]
    last = (0, 0)
    last_ang = 0.0
    for k in range(1, radius + 1):
        ring = hex_ring_cycle(k)
        candidates: List[Tuple[float, int]] = []
        for i, p in enumerate(ring):
            if is_neighbor_hex(last, p):
                ang = angle01(*projected_xy(p))
                delta = ang - last_ang
                if delta <= 0:
                    delta += 2.0 * math.pi
                candidates.append((delta, i))
        if not candidates:
            raise RuntimeError(f'hex spiral could not connect ring {k} to previous ring')
        _, idx = min(candidates)
        ring = rotate(ring, idx)
        out.extend(ring)
        last = ring[-1]
        last_ang = angle01(*projected_xy(last))
    return out


def points_for(geometry: str, outer: int, order: str) -> List[Coord]:
    if geometry == 'square':
        if order == 'spiral':
            return square_spiral_points(outer)
        pts = [(a, b) for b in range(-outer, outer + 1) for a in range(-outer, outer + 1)]
        pts.sort(key=square_key)
        return pts
    if geometry == 'hex':
        if order == 'spiral':
            return hex_spiral_points(outer)
        pts = hex_ball(outer)
        pts.sort(key=hex_distatan_key)
        return pts
    raise ValueError(geometry)


def attacks_for(geometry: str) -> Tuple[Coord, ...]:
    if geometry == 'square':
        return SQUARE_KNIGHT
    if geometry == 'hex':
        # Hex short-knight move: step forward one hex edge, turn consistently
        # 60 degrees counterclockwise, then step forward one more edge.
        # Cycling through the six initial directions gives six attacked sites.
        return tuple(add(HEX_DIRS[i], HEX_DIRS[(i + 1) % 6]) for i in range(6))
    raise ValueError(geometry)


def square_visible(p: Coord, radius: int) -> bool:
    a, b = p
    return -radius <= a <= radius and -radius <= b <= radius


def square_trusted(p: Coord, trusted: int) -> bool:
    a, b = p
    return a * a + b * b <= trusted * trusted


def hex_visible(p: Coord, radius: int) -> bool:
    return axial_distance(p) <= radius


def make_geometry(geometry: str, order: str, radius: int, trusted_radius: int | None = None, outer_radius: int | None = None) -> Tuple[List[Coord], Metadata]:
    if geometry == 'square':
        if trusted_radius is None:
            trusted_radius = math.ceil(radius * math.sqrt(2.0))
        if outer_radius is None:
            outer_radius = trusted_radius
        pts = points_for('square', outer_radius, order)
        trusted_last = max(i for i, p in enumerate(pts) if square_trusted(p, trusted_radius))
        attack = 'square8'
        visible = 'square'
    elif geometry == 'hex':
        if trusted_radius is None:
            trusted_radius = radius + 3
        if outer_radius is None:
            outer_radius = trusted_radius
        pts = points_for('hex', outer_radius, order)
        trusted_last = max(i for i, p in enumerate(pts) if axial_distance(p) <= trusted_radius)
        attack = 'hex6'
        visible = 'hex-ball'
    else:
        raise ValueError(geometry)
    md = Metadata('03', 'knight-quadrant', 'geometry', geometry, attack, order, '', radius, trusted_radius, outer_radius, visible, trusted_last)
    return pts, md


def write_meta(out, md: Metadata) -> None:
    for k, v in md.__dict__.items():
        out.write(f'# {k}={v}\n')


def read_text_csv(path: str) -> Tuple[dict, List[dict]]:
    meta: Dict[str, str] = {}
    lines: List[str] = []
    fh = sys.stdin if path == '-' else open(path, newline='')
    with fh:
        for line in fh:
            if line.startswith('#'):
                text = line[1:].strip()
                if '=' in text:
                    k, v = text.split('=', 1)
                    meta[k.strip()] = v.strip()
            else:
                lines.append(line)
    rows = list(csv.DictReader(lines))
    return meta, rows


def metadata_from_meta(meta: dict) -> Metadata:
    return Metadata(
        meta['artifact_index'],
        meta['artifact_name'],
        meta.get('kind', 'moves'),
        meta['geometry'],
        meta['attack'],
        meta['order'],
        meta.get('colors', ''),
        int(meta['radius']),
        int(meta['trusted_radius']),
        int(meta['outer_radius']),
        meta['visible_shape'],
        int(meta['trusted_last_index']),
    )


def read_points(path: str) -> Tuple[Metadata, List[Coord]]:
    meta, rows = read_text_csv(path)
    md = metadata_from_meta(meta)
    pts = [(int(r['a']), int(r['b'])) for r in rows]
    return md, pts


def read_moves(path: str) -> Tuple[Metadata, List[dict]]:
    meta, rows = read_text_csv(path)
    return metadata_from_meta(meta), rows


def write_geometry(args) -> None:
    pts, md = make_geometry(args.geometry, args.order, args.radius, args.trusted_radius, args.outer_radius)
    out = sys.stdout
    write_meta(out, md)
    writer = csv.DictWriter(out, fieldnames=POINT_FIELDS)
    writer.writeheader()
    for i, (a, b) in enumerate(pts):
        writer.writerow({'order_index': i, 'a': a, 'b': b})


def attacked(cell: Coord, color: int, owner_at: Dict[Coord, int], attacks: Sequence[Coord], ncolors: int) -> bool:
    a, b = cell
    self_attack = (ncolors == 1)
    for da, db in attacks:
        owner = owner_at.get((a + da, b + db))
        if owner is None:
            continue
        if self_attack or owner != color:
            return True
    return False


def legal(cell: Coord, color: int, owner_at: Dict[Coord, int], attacks: Sequence[Coord], ncolors: int) -> bool:
    return cell not in owner_at and not attacked(cell, color, owner_at, attacks, ncolors)


def validate_colors(colors: str) -> None:
    if not colors:
        raise SystemExit('need at least one color')
    if len(set(colors)) != len(colors):
        raise SystemExit('colors must not repeat')
    bad = [c for c in colors if c not in COLOR_RGB]
    if bad:
        raise SystemExit('unsupported colors: ' + ''.join(bad))


def load_points_from_args(args) -> Tuple[Metadata, List[Coord]]:
    if getattr(args, 'points', None):
        return read_points(args.points)
    return make_geometry(args.geometry, args.order, args.radius, args.trusted_radius, args.outer_radius)


def generate_moves(pts: Sequence[Coord], md: Metadata, colors: str) -> List[dict]:
    validate_colors(colors)
    attacks = attacks_for(md.geometry)
    ncolors = len(colors)
    owner_at: Dict[Coord, int] = {}
    cursor = [-1] * ncolors
    moves: List[dict] = []
    while any(c <= md.trusted_last_index for c in cursor):
        for color in range(ncolors):
            start = cursor[color] + 1
            placed = False
            for i in range(start, len(pts)):
                cell = pts[i]
                cursor[color] = i
                if not legal(cell, color, owner_at, attacks, ncolors):
                    continue
                owner_at[cell] = color
                moves.append({
                    'move': len(moves) + 1,
                    'color_index': color,
                    'color': colors[color],
                    'order_index': i,
                    'a': cell[0],
                    'b': cell[1],
                    'cursor_start': start,
                    'cursor_after': i,
                })
                placed = True
                break
            if not placed:
                cursor[color] = len(pts)
    return moves


def write_moves_to_path(path: Path, md: Metadata, colors: str, moves: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    md2 = Metadata(md.artifact_index, md.artifact_name, 'moves', md.geometry, md.attack, md.order, colors, md.radius, md.trusted_radius, md.outer_radius, md.visible_shape, md.trusted_last_index)
    with open(path, 'w', newline='') as out:
        write_meta(out, md2)
        writer = csv.DictWriter(out, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(moves)


def write_data(args) -> None:
    md, pts = load_points_from_args(args)
    moves = generate_moves(pts, md, args.colors)
    md2 = Metadata(md.artifact_index, md.artifact_name, 'moves', md.geometry, md.attack, md.order, args.colors, md.radius, md.trusted_radius, md.outer_radius, md.visible_shape, md.trusted_last_index)
    out = sys.stdout
    write_meta(out, md2)
    writer = csv.DictWriter(out, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(moves)


def batch_data(args) -> None:
    md, pts = read_points(args.points)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    colorsets = [s for s in args.colorsets.split(',') if s]
    for colors in colorsets:
        moves = generate_moves(pts, md, colors)
        path = out_dir / f'{colors}_{md.geometry}_{md.order}_r{md.radius}.csv'
        write_moves_to_path(path, md, colors, moves)
        if args.check_fast:
            class A: pass
            a = A()
            a.csv = str(path)
            a.points = args.points
            check_fast(a, quiet=True)


def check_fast(args, quiet: bool = False) -> None:
    md, rows = read_moves(args.csv)
    if getattr(args, 'points', None):
        pmd, pts = read_points(args.points)
        if (pmd.geometry, pmd.order, pmd.radius, pmd.trusted_last_index) != (md.geometry, md.order, md.radius, md.trusted_last_index):
            raise SystemExit('points metadata mismatch')
    else:
        pts, _ = make_geometry(md.geometry, md.order, md.radius, md.trusted_radius, md.outer_radius)
    attacks = attacks_for(md.geometry)
    ncolors = len(md.colors)
    owner_at: Dict[Coord, int] = {}
    cursor = [-1] * ncolors
    for pos, row in enumerate(rows):
        move = int(row['move'])
        color = int(row['color_index'])
        idx = int(row['order_index'])
        cell = (int(row['a']), int(row['b']))
        if move != pos + 1:
            raise SystemExit(f'row {pos + 1}: move number mismatch')
        if row['color'] != md.colors[color]:
            raise SystemExit(f'move {move}: wrong color letter')
        if idx <= cursor[color]:
            raise SystemExit(f'move {move}: non-increasing cursor')
        if idx >= len(pts) or pts[idx] != cell:
            raise SystemExit(f'move {move}: order index mismatch')
        if not legal(cell, color, owner_at, attacks, ncolors):
            raise SystemExit(f'move {move}: illegal cell')
        owner_at[cell] = color
        cursor[color] = idx
    if not quiet:
        print(f'FAST PASS {args.csv}: {len(rows)} moves, geometry={md.geometry}, order={md.order}, colors={md.colors}')


def read_points_or_rebuild_from_move(md: Metadata, points_path: str | None) -> List[Coord]:
    if points_path:
        pmd, pts = read_points(points_path)
        if (pmd.geometry, pmd.order, pmd.radius) != (md.geometry, md.order, md.radius):
            raise SystemExit('points metadata mismatch')
        return pts
    pts, _ = make_geometry(md.geometry, md.order, md.radius, md.trusted_radius, md.outer_radius)
    return pts


def square_png(md: Metadata, rows: List[dict], out: str, scale: int) -> None:
    from PIL import Image
    side = 2 * md.radius + 1
    img = Image.new('RGB', (side, side), (255, 255, 255))
    pix = img.load()
    for row in rows:
        a, b = int(row['a']), int(row['b'])
        if square_visible((a, b), md.radius):
            pix[a + md.radius, md.radius - b] = COLOR_RGB[row['color']]
    if scale != 1:
        img = img.resize((side * scale, side * scale), Image.Resampling.NEAREST)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f'wrote {out}')


def hex_center(p: Coord, cell: float) -> Tuple[float, float]:
    x, y = projected_xy(p)
    return (math.sqrt(3.0) * cell * x, 1.5 * cell * p[1])


def hex_poly(cx: float, cy: float, cell: float) -> List[Tuple[float, float]]:
    return [
        (
            cx + cell * math.cos(math.radians(30 + 60 * k)),
            cy + cell * math.sin(math.radians(30 + 60 * k)),
        )
        for k in range(6)
    ]


def svg_header(w: float, h: float) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}" height="{h:.1f}" viewBox="0 0 {w:.1f} {h:.1f}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]


def hex_image_svg(md: Metadata, rows: List[dict], pts: List[Coord], out: str, cell: float) -> None:
    by_cell = {(int(r['a']), int(r['b'])): r for r in rows if hex_visible((int(r['a']), int(r['b'])), md.radius)}
    vis = [p for p in pts if hex_visible(p, md.radius) and p in by_cell]
    items = []
    minx = miny = 1e100
    maxx = maxy = -1e100
    for p in vis:
        cx, cy = hex_center(p, cell)
        poly = hex_poly(cx, cy, cell)
        row = by_cell[p]
        items.append((row, poly))
        for x, y in poly:
            minx = min(minx, x)
            miny = min(miny, y)
            maxx = max(maxx, x)
            maxy = max(maxy, y)
    pad = 8
    def tx(x: float) -> float: return x - minx + pad
    def ty(y: float) -> float: return maxy - y + pad
    lines = svg_header(maxx - minx + 2 * pad, maxy - miny + 2 * pad)
    for row, poly in items:
        pts_str = ' '.join(f'{tx(x):.2f},{ty(y):.2f}' for x, y in poly)
        col = COLOR_STROKE[row['color']]
        lines.append(f'<polygon points="{pts_str}" fill="{col}" stroke="{col}" stroke-width="1"/>')
    lines.append('</svg>')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out}')


def render_image(args) -> None:
    md, rows = read_moves(args.csv)
    pts = read_points_or_rebuild_from_move(md, getattr(args, 'points', None))
    if md.geometry == 'square':
        square_png(md, rows, args.out, args.scale)
    else:
        hex_image_svg(md, rows, pts, args.out, args.cell)


def debug_square(md: Metadata, rows: List[dict], pts: List[Coord], out: str, radius: int, cell: float) -> None:
    by_cell = {(int(r['a']), int(r['b'])): r for r in rows if square_visible((int(r['a']), int(r['b'])), radius)}
    order_index = {p: i for i, p in enumerate(pts)}
    pad = 20
    w = h = (2 * radius + 1) * cell + 2 * pad
    lines = svg_header(w, h)
    lines.append('<style>.num{font-family:monospace;font-size:10px;text-anchor:middle;dominant-baseline:central}.small{font-family:monospace;font-size:7px;fill:#555;text-anchor:end}</style>')
    for b in range(radius, -radius - 1, -1):
        for a in range(-radius, radius + 1):
            x = pad + (a + radius) * cell
            y = pad + (radius - b) * cell
            row = by_cell.get((a, b))
            lines.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="white" stroke="#ccc" stroke-width="1"/>')
            lines.append(f'<text class="num" x="{x + cell / 2}" y="{y + cell / 2}">{order_index[(a, b)]}</text>')
            if row is not None:
                col = COLOR_STROKE[row['color']]
                lines.append(f'<circle cx="{x + cell / 2}" cy="{y + cell / 2}" r="{cell * 0.38:.1f}" fill="none" stroke="{col}" stroke-width="2.5"/>')
                lines.append(f'<text class="small" x="{x + cell - 3}" y="{y + cell - 4}">{row["move"]}</text>')
    lines.append('</svg>')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out}')


def debug_hex(md: Metadata, rows: List[dict], pts: List[Coord], out: str, radius: int, cell: float) -> None:
    vis = [p for p in pts if hex_visible(p, radius)]
    order_index = {p: i for i, p in enumerate(pts)}
    by_cell = {(int(r['a']), int(r['b'])): r for r in rows if hex_visible((int(r['a']), int(r['b'])), radius)}
    items = []
    minx = miny = 1e100
    maxx = maxy = -1e100
    for p in vis:
        cx, cy = hex_center(p, cell)
        poly = hex_poly(cx, cy, cell)
        items.append((p, cx, cy, poly, by_cell.get(p)))
        for x, y in poly:
            minx = min(minx, x)
            miny = min(miny, y)
            maxx = max(maxx, x)
            maxy = max(maxy, y)
    pad = 12
    def tx(x: float) -> float: return x - minx + pad
    def ty(y: float) -> float: return maxy - y + pad
    lines = svg_header(maxx - minx + 2 * pad, maxy - miny + 2 * pad)
    lines.append('<style>.num{font-family:monospace;font-size:8px;text-anchor:middle;dominant-baseline:central}.small{font-family:monospace;font-size:7px;fill:#555;text-anchor:end}</style>')
    for p, cx, cy, poly, row in items:
        pts_str = ' '.join(f'{tx(x):.2f},{ty(y):.2f}' for x, y in poly)
        lines.append(f'<polygon points="{pts_str}" fill="white" stroke="#ccc" stroke-width="1"/>')
        if row is not None:
            col = COLOR_STROKE[row['color']]
            lines.append(f'<circle cx="{tx(cx):.2f}" cy="{ty(cy):.2f}" r="{cell * 0.58:.1f}" fill="none" stroke="{col}" stroke-width="2.5"/>')
            lines.append(f'<text class="small" x="{tx(cx + cell * 0.55):.2f}" y="{ty(cy - cell * 0.35):.2f}">{row["move"]}</text>')
        lines.append(f'<text class="num" x="{tx(cx):.2f}" y="{ty(cy):.2f}">{order_index[p]}</text>')
    lines.append('</svg>')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out}')


def render_debug(args) -> None:
    md, rows = read_moves(args.csv)
    pts = read_points_or_rebuild_from_move(md, getattr(args, 'points', None))
    if md.geometry == 'square':
        debug_square(md, rows, pts, args.out, args.radius, args.cell)
    else:
        debug_hex(md, rows, pts, args.out, args.radius, args.cell)


def check_hex_knight(args=None) -> None:
    moves = attacks_for('hex')
    if len(moves) != 6:
        raise SystemExit('hex short-knight does not have 6 distinct moves')
    if len(set(moves)) != 6:
        raise SystemExit('hex short-knight moves are not distinct')
    for i, mv in enumerate(moves):
        expected = add(HEX_DIRS[i], HEX_DIRS[(i + 1) % 6])
        if mv != expected:
            raise SystemExit(f'bad hex short-knight move at direction {i}: {mv} != {expected}')
        if (-mv[0], -mv[1]) not in moves:
            raise SystemExit('hex short-knight is not centrally symmetric')
    print('PASS hex short-knight: 6 moves, symmetric, 1+turn+1 construction')


def check_hex_spiral(args=None) -> None:
    for radius in range(1, 10):
        pts = hex_spiral_points(radius)
        for i in range(1, len(pts)):
            if not is_neighbor_hex(pts[i - 1], pts[i]):
                raise SystemExit(f'hex spiral adjacency failure at radius {radius}, step {i}: {pts[i - 1]} -> {pts[i]}')
    print('PASS hex spiral: every step touches a nearest neighbor on tested radii 1..9')


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('geometry')
    p.add_argument('--geometry', choices=['square', 'hex'], required=True)
    p.add_argument('--order', choices=['spiral', 'dist-atan'], required=True)
    p.add_argument('--radius', type=int, required=True)
    p.add_argument('--trusted-radius', type=int, default=None)
    p.add_argument('--outer-radius', type=int, default=None)
    p.set_defaults(func=write_geometry)

    p = sub.add_parser('data')
    p.add_argument('--geometry', choices=['square', 'hex'])
    p.add_argument('--order', choices=['spiral', 'dist-atan'])
    p.add_argument('--radius', type=int)
    p.add_argument('--trusted-radius', type=int, default=None)
    p.add_argument('--outer-radius', type=int, default=None)
    p.add_argument('--points')
    p.add_argument('--colors', required=True)
    p.set_defaults(func=write_data)

    p = sub.add_parser('batch-data')
    p.add_argument('--points', required=True)
    p.add_argument('--colorsets', required=True)
    p.add_argument('--out-dir', required=True)
    p.add_argument('--check-fast', action='store_true')
    p.set_defaults(func=batch_data)

    p = sub.add_parser('check-fast')
    p.add_argument('csv')
    p.add_argument('--points')
    p.set_defaults(func=check_fast)

    p = sub.add_parser('image')
    p.add_argument('csv')
    p.add_argument('--points')
    p.add_argument('--out', required=True)
    p.add_argument('--scale', type=int, default=1)
    p.add_argument('--cell', type=float, default=6.0)
    p.set_defaults(func=render_image)

    p = sub.add_parser('debug-svg')
    p.add_argument('csv')
    p.add_argument('--points')
    p.add_argument('--radius', type=int, required=True)
    p.add_argument('--cell', type=float, default=28.0)
    p.add_argument('--out', required=True)
    p.set_defaults(func=render_debug)

    p = sub.add_parser('check-hex-knight')
    p.set_defaults(func=check_hex_knight)

    p = sub.add_parser('check-hex-spiral')
    p.set_defaults(func=check_hex_spiral)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
