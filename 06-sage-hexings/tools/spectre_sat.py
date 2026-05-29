#!/usr/bin/env python3
"""
spectre_sat.py

DIMACS SAT generator / decoder for the reduced two-hex model used in the
current 7-hex supertile experiments.

This is intentionally solver-agnostic:
  python3 spectre_sat.py cnf --radius 10 --out out/r10.cnf
  kissat out/r10.cnf out/r10.model
  python3 spectre_sat.py decode --radius 10 --model out/r10.model --out out/r10.dat
  python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg

Supported external solvers by command name:
  kissat, cadical, minisat, glucose, cryptominisat5, picosat

The CNF fixes the central 7-hex supertile and asks for a legal assignment of
H0/H1 orientations on a finite hex ball.
"""

from __future__ import annotations

import argparse
import itertools
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

H1 = ("H","A","D","E","B","G")
H0 = ("C","A","B","F","G","I")

EDGE_RULES = {
    (("A","B"),("B","G")),(("A","B"),("C","A")),(("A","B"),("G","H")),
    (("A","B"),("G","I")),(("A","B"),("I","C")),(("A","D"),("C","A")),
    (("B","F"),("C","A")),(("B","F"),("D","E")),(("B","F"),("F","G")),
    (("B","G"),("A","B")),(("B","G"),("E","B")),(("C","A"),("A","B")),
    (("C","A"),("A","D")),(("C","A"),("B","F")),(("C","A"),("G","I")),
    (("C","A"),("H","A")),(("D","E"),("B","F")),(("D","E"),("G","I")),
    (("E","B"),("B","G")),(("E","B"),("G","I")),(("F","G"),("B","F")),
    (("F","G"),("G","I")),(("F","G"),("I","C")),(("G","H"),("A","B")),
    (("G","I"),("A","B")),(("G","I"),("C","A")),(("G","I"),("D","E")),
    (("G","I"),("E","B")),(("G","I"),("F","G")),(("H","A"),("C","A")),
    (("I","C"),("A","B")),(("I","C"),("F","G")),(("I","C"),("I","C")),
}

VERTEX_RULES_RAW = """
A A C
A A H
A B C
A B G
A B I
A G I
B B B
B B G
B G E
B G G
B I E
C F D
C F F
C I D
C I F
E G I
F F F
G G G
""".strip().splitlines()

DIRS = {
    0:(1,0), 1:(0,1), 2:(-1,1),
    3:(-1,0), 4:(0,-1), 5:(1,-1),
}

ANGLES = [-30, 30, 90, 150, 210, 270]


def canon3(t):
    t = tuple(t)
    return min(t[i:] + t[:i] for i in range(3))


VERTEX_RULES = {canon3(x.split()) for x in VERTEX_RULES_RAW}


def add(p, d):
    dq, dr = DIRS[d]
    return (p[0] + dq, p[1] + dr)


def hdist(p):
    q, r = p
    return max(abs(q), abs(r), abs(-q-r))


def hex_ball(radius):
    return sorted(
        (q, r)
        for q in range(-radius, radius + 1)
        for r in range(-radius, radius + 1)
        if hdist((q, r)) <= radius
    )


ORIENTS = []
for name, tile in [("H0", H0), ("H1", H1)]:
    for rot in range(6):
        labs = tuple(tile[(j - rot) % 6] for j in range(6))
        edges = tuple((labs[j], labs[(j+1) % 6]) for j in range(6))
        ORIENTS.append((name, rot, labs, edges))


def oid(name, rot):
    for i, o in enumerate(ORIENTS):
        if o[0] == name and o[1] == rot:
            return i
    raise KeyError((name, rot))


BASE = {
    (-1,0): oid("H0",2),
    (0,-1): oid("H0",0),
    (0,0): oid("H1",0),
    (0,1): oid("H0",4),
    (1,-1): oid("H0",1),
    (1,0): oid("H0",3),
    (2,-1): oid("H0",2),
}


def edge_ok(a, d, b):
    return (ORIENTS[a][3][d % 6], ORIENTS[b][3][(d+3) % 6]) in EDGE_RULES


def vertex_ok(a_prev, a_mid, a_next, j):
    # Around vertex j of middle cell:
    #   middle label j, previous neighbor contributes j+2, next neighbor contributes j+4.
    tri = canon3((
        ORIENTS[a_mid][2][j % 6],
        ORIENTS[a_prev][2][(j+2) % 6],
        ORIENTS[a_next][2][(j+4) % 6],
    ))
    return tri in VERTEX_RULES


class CNF:
    def __init__(self):
        self.clauses = []
        self.var_count = 0

    def new_var(self):
        self.var_count += 1
        return self.var_count

    def add(self, lits):
        self.clauses.append(list(lits))

    def exactly_one(self, lits):
        self.add(lits)
        for a, b in itertools.combinations(lits, 2):
            self.add([-a, -b])

    def write(self, path: Path):
        with path.open("w") as f:
            f.write(f"p cnf {self.var_count} {len(self.clauses)}\n")
            for c in self.clauses:
                f.write(" ".join(map(str, c)) + " 0\n")


def make_problem(radius: int):
    cells = hex_ball(radius)
    cellset = set(cells)
    cnf = CNF()

    var = {}
    for p in cells:
        for a in range(12):
            var[(p, a)] = cnf.new_var()

    # exactly one orientation per cell
    for p in cells:
        cnf.exactly_one([var[(p, a)] for a in range(12)])

    # fix central 7-block
    for p, a in BASE.items():
        if p not in cellset:
            raise ValueError(f"radius {radius} is too small for base cell {p}")
        cnf.add([var[(p, a)]])

    # edge constraints: for each undirected adjacent pair, forbid bad orientation pairs.
    # Use d=0,1,2 only to avoid duplicating undirected edges.
    for p in cells:
        for d in [0, 1, 2]:
            q = add(p, d)
            if q not in cellset:
                continue
            for a in range(12):
                for b in range(12):
                    if not edge_ok(a, d, b):
                        cnf.add([-var[(p, a)], -var[(q, b)]])

    # vertex constraints: for each occupied triple around a vertex of a cell,
    # forbid illegal orientation triples.
    #
    # This duplicates some geometric vertices, but that is okay for SAT.
    for p in cells:
        for j in range(6):
            prev = add(p, (j-1) % 6)
            nxt = add(p, j)
            if prev not in cellset or nxt not in cellset:
                continue
            for a_mid in range(12):
                for a_prev in range(12):
                    for a_next in range(12):
                        if not vertex_ok(a_prev, a_mid, a_next, j):
                            cnf.add([
                                -var[(p, a_mid)],
                                -var[(prev, a_prev)],
                                -var[(nxt, a_next)],
                            ])

    return cnf, cells, var


def write_map(path: Path, cells, var):
    with path.open("w") as f:
        f.write("# var q r orient tile rot labels\n")
        for p in cells:
            q, r = p
            for a in range(12):
                name, rot, labs, _edges = ORIENTS[a]
                f.write(f"{var[(p,a)]} {q} {r} {a} {name} {rot} {''.join(labs)}\n")


def parse_model(path: Path):
    vals = set()
    text = path.read_text(errors="replace").split()
    # accept DIMACS-style v lines or plain integers.
    for tok in text:
        if tok in {"v", "s", "SATISFIABLE", "SAT", "UNKNOWN"}:
            continue
        try:
            n = int(tok)
        except ValueError:
            continue
        if n > 0:
            vals.add(n)
    return vals


def load_map(path: Path):
    table = {}
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        v, q, r, a, name, rot, labels = line.split()
        table[int(v)] = (int(q), int(r), int(a), name, int(rot), labels)
    return table


def cmd_cnf(args):
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cnf, cells, var = make_problem(args.radius)
    cnf.write(out)
    map_path = Path(args.map) if args.map else out.with_suffix(".map")
    write_map(map_path, cells, var)
    print(f"wrote {out}")
    print(f"wrote {map_path}")
    print(f"radius={args.radius} cells={len(cells)} vars={cnf.var_count} clauses={len(cnf.clauses)}")


def find_solver(preferred=None):
    names = []
    if preferred:
        names.append(preferred)
    names += ["kissat", "cadical", "minisat", "glucose", "cryptominisat5", "picosat"]
    for n in names:
        p = shutil.which(n)
        if p:
            return n, p
    return None, None


def cmd_solve(args):
    cnf = Path(args.cnf)
    model = Path(args.model)
    model.parent.mkdir(parents=True, exist_ok=True)
    name, exe = find_solver(args.solver)
    if not exe:
        raise SystemExit("No supported SAT solver found on PATH.")

    # Solver output conventions vary, so capture stdout and write it as model text.
    print(f"running {name} on {cnf}")
    if name == "minisat":
        proc = subprocess.run([exe, str(cnf), str(model)], text=True, capture_output=True)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    elif name in {"kissat", "cadical", "glucose", "cryptominisat5", "picosat"}:
        proc = subprocess.run([exe, str(cnf)], text=True, capture_output=True)
        model.write_text(proc.stdout)
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    else:
        raise SystemExit(f"unsupported solver wrapper: {name}")

    print(f"model/output written to {model}")


def cmd_decode(args):
    map_path = Path(args.map) if args.map else Path(args.model).with_suffix(".map")
    vals = parse_model(Path(args.model))
    table = load_map(map_path)

    chosen = []
    for v in sorted(vals):
        if v in table:
            chosen.append(table[v])

    if not chosen:
        raise SystemExit("No positive mapped variables found. Is the instance SAT and map path correct?")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("# q r orient tile rot labels\n")
        for q, r, a, name, rot, labels in sorted(chosen):
            f.write(f"{q} {r} {a} {name} {rot} {labels}\n")
    print(f"wrote {out}")
    print(f"cells={len(chosen)}")


def read_dat(path: Path):
    pl = {}
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        q, r, a, name, rot, labels = line.split()
        pl[(int(q), int(r))] = int(a)
    return pl


def rot_pos(p, k):
    q, r = p
    for _ in range(k % 6):
        q, r = -r, q+r
    return (q, r)


def rot_oid(a, k):
    return oid(ORIENTS[a][0], (ORIENTS[a][1] + k) % 6)


def block(k, t):
    tq, tr = t
    return {
        (rot_pos(p, k)[0] + tq, rot_pos(p, k)[1] + tr): rot_oid(a, k)
        for p, a in BASE.items()
    }


def find_embedded_blocks(pl):
    qs = [q for q, r in pl]
    rs = [r for q, r in pl]
    out = []
    for k in range(6):
        for tq in range(min(qs)-5, max(qs)+6):
            for tr in range(min(rs)-5, max(rs)+6):
                b = block(k, (tq, tr))
                if set(b).issubset(pl) and all(pl[p] == a for p, a in b.items()):
                    out.append({"k": k, "t": (tq, tr), "block": b, "cells": frozenset(b)})
    uniq = {}
    for b in out:
        uniq[(b["k"], b["t"], b["cells"])] = b
    return list(uniq.values())


def xy(p):
    q, r = p
    return (math.sqrt(3) * (q + r/2), 1.5 * r)


def hex_vertices(p, R=1.0):
    cx, cy = xy(p)
    return [
        (cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
        for a in ANGLES
    ]


def outline(ax, cells, color="red", lw=2.3):
    cells = set(cells)
    for p in cells:
        pts = hex_vertices(p)
        for d in range(6):
            if add(p, d) not in cells:
                (x1, y1), (x2, y2) = pts[d], pts[(d+1) % 6]
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw)


def cmd_draw(args):
    # Dependency-free SVG renderer. No matplotlib required.
    #
    # Default:
    #   - draw the base tiling
    #   - draw overlap fill / darkening
    #   - draw every embedded 7-block red outline
    #
    # Important SVG convention:
    #   stroke width is in geometry units.  A hex edge has length about 1,
    #   so red outline widths must be around 0.025..0.070, not 1.4.
    from collections import defaultdict

    pl = read_dat(Path(args.dat))
    blocks = find_embedded_blocks(pl)

    overlap = defaultdict(int)
    for b in blocks:
        for p in b["cells"]:
            overlap[p] += 1
    max_overlap = max(overlap.values()) if overlap else 1

    def poly_points(points):
        return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)

    def svg_hex(p, fill, stroke="black", sw=0.028, opacity=1.0):
        pts = hex_vertices(p)
        return (
            f'<polygon points="{poly_points(pts)}" '
            f'fill="{fill}" fill-opacity="{opacity:.3f}" '
            f'stroke="{stroke}" stroke-width="{sw:.3f}" '
            f'stroke-linejoin="miter" />'
        )

    xs, ys = [], []
    for p in pl:
        for x, y in hex_vertices(p):
            xs.append(x); ys.append(y)

    pad = 1.0
    minx, maxx = min(xs) - pad, max(xs) + pad
    miny, maxy = min(ys) - pad, max(ys) + pad
    width, height = maxx - minx, maxy - miny

    fill = {"H0": "#f6ead2", "H1": "#dce8f6"}
    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{minx:.3f} {miny:.3f} {width:.3f} {height:.3f}" '
        f'width="{width*45:.0f}" height="{height*45:.0f}">'
    )
    lines.append(
        '<rect x="{:.3f}" y="{:.3f}" width="{:.3f}" height="{:.3f}" fill="white" />'
        .format(minx, miny, width, height)
    )

    # Base hexes.
    lines.append('<g id="hexes">')
    for p, a in sorted(pl.items()):
        name = ORIENTS[a][0]
        lines.append(svg_hex(p, fill[name], "black", 0.028, 1.0))
    lines.append('</g>')

    # Default overlap fill, restored.
    if args.overlap_fill:
        lines.append('<g id="overlap-shading">')
        for p, count in sorted(overlap.items()):
            if count < args.overlap_min:
                continue
            alpha = args.overlap_alpha * (count / max_overlap)
            pts = hex_vertices(p)
            lines.append(
                f'<polygon points="{poly_points(pts)}" '
                f'fill="black" fill-opacity="{alpha:.3f}" stroke="none" />'
            )
        lines.append('</g>')

    # Red outlines for every embedded 7-block.
    lines.append(
        '<g id="supertile-outlines" fill="none" stroke="red" '
        'stroke-linecap="butt" stroke-linejoin="miter" '
        f'stroke-opacity="{args.outline_alpha:.3f}">'
    )
    for b in blocks:
        cells = set(b["cells"])
        for p in sorted(cells):
            pts = hex_vertices(p)
            for d in range(6):
                if add(p, d) not in cells:
                    (x1, y1), (x2, y2) = pts[d], pts[(d+1) % 6]
                    lines.append(
                        f'<line x1="{x1:.3f}" y1="{y1:.3f}" '
                        f'x2="{x2:.3f}" y2="{y2:.3f}" '
                        f'stroke-width="{args.linewidth:.3f}" />'
                    )
    lines.append('</g>')

    if args.overlap_numbers:
        lines.append(
            '<g id="overlap-counts" font-family="monospace" font-size="0.32" '
            'text-anchor="middle" dominant-baseline="central" fill="purple">'
        )
        for p, count in sorted(overlap.items()):
            if count >= args.overlap_min:
                cx, cy = xy(p)
                lines.append(f'<text x="{cx:.3f}" y="{cy:.3f}">{count}</text>')
        lines.append('</g>')

    if args.labels:
        lines.append(
            '<g id="labels" font-family="monospace" font-size="0.24" '
            'text-anchor="middle" dominant-baseline="central" fill="black">'
        )
        for p, a in sorted(pl.items()):
            cx, cy = xy(p)
            lines.append(f'<text x="{cx:.3f}" y="{cy:.3f}">{ORIENTS[a][0]}</text>')
        lines.append('</g>')

    lines.append('</svg>')

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"wrote {out}")
    print(f"cells={len(pl)} embedded_7_blocks={len(blocks)} max_overlap={max_overlap}")


def cmd_all(args):
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cnf = outdir / f"r{args.radius}.cnf"
    mp = outdir / f"r{args.radius}.map"
    mdl = outdir / f"r{args.radius}.model"
    dat = outdir / f"r{args.radius}.dat"
    svg = outdir / f"r{args.radius}.svg"

    cmd_cnf(argparse.Namespace(radius=args.radius, out=str(cnf), map=str(mp)))
    name, exe = find_solver(args.solver)
    if not exe:
        print("No solver found; generated CNF only.")
        return
    cmd_solve(argparse.Namespace(cnf=str(cnf), model=str(mdl), solver=args.solver))
    cmd_decode(argparse.Namespace(model=str(mdl), map=str(mp), out=str(dat)))
    cmd_draw(argparse.Namespace(dat=str(dat), out=str(svg), linewidth=args.linewidth,
                                dpi=200, width=18, height=16, labels=False,
                                overlap_fill=True, overlap_alpha=0.12,
                                overlap_min=1, overlap_numbers=False,
                                outline_alpha=1.0))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)

    p = sub.add_parser("cnf")
    p.add_argument("--radius", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--map")
    p.set_defaults(func=cmd_cnf)

    p = sub.add_parser("solve")
    p.add_argument("--cnf", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--solver")
    p.set_defaults(func=cmd_solve)

    p = sub.add_parser("decode")
    p.add_argument("--model", required=True)
    p.add_argument("--map")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_decode)

    p = sub.add_parser("draw")
    p.add_argument("--dat", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--linewidth", type=float, default=0.070,
                   help="red outline stroke width in SVG coordinate units; try 0.045..0.100")
    p.add_argument("--dpi", type=int, default=250)      # ignored by SVG renderer
    p.add_argument("--width", type=float, default=18)   # ignored by SVG renderer
    p.add_argument("--height", type=float, default=16)  # ignored by SVG renderer
    p.add_argument("--labels", action="store_true")
    p.add_argument("--overlap-fill", dest="overlap_fill", action="store_true", default=True,
                   help="enable red overlap fill / darkening; default on")
    p.add_argument("--no-overlap-fill", dest="overlap_fill", action="store_false",
                   help="disable red overlap fill / darkening")
    p.add_argument("--overlap-alpha", type=float, default=0.18,
                   help="max alpha scale for overlap fill")
    p.add_argument("--overlap-min", type=int, default=1,
                   help="minimum overlap count to shade or label")
    p.add_argument("--overlap-numbers", action="store_true",
                   help="write overlap counts as purple numbers")
    p.add_argument("--outline-alpha", type=float, default=1.0,
                   help="red outline opacity")
    p.set_defaults(func=cmd_draw)

    p = sub.add_parser("all")
    p.add_argument("--radius", type=int, required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--solver")
    p.add_argument("--linewidth", type=float, default=0.045)
    p.set_defaults(func=cmd_all)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
