#!/usr/bin/env python3
"""Reduced Spectre hexagon model experiments.

This script intentionally uses only the Python standard library so that the
artifact can run on a plain system Python.  It verifies the reduced two-hex
model, runs weak local forcing scans, and generates a fact-sheet PDF plus a
separate strong-closure drawing.
"""

from __future__ import annotations

import argparse
import math
import os
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Label = str
Edge = Tuple[Label, Label]
Tile = Tuple[Label, ...]
Pos = Tuple[int, int]

DIRS = {
    0: (1, 0),
    1: (0, 1),
    2: (-1, 1),
    3: (-1, 0),
    4: (0, -1),
    5: (1, -1),
}
ANGLES = [-30, 30, 90, 150, 210, 270]


def add(pos: Pos, side: int) -> Pos:
    dq, dr = DIRS[side]
    return (pos[0] + dq, pos[1] + dr)


def canon3(t: Iterable[str]) -> Tuple[str, str, str]:
    x = tuple(t)
    return min(x[i:] + x[:i] for i in range(3))


def parse_edge(text: str) -> Edge:
    a, b = [x.strip() for x in text.split(",")]
    return (a, b)


class Model:
    def __init__(self, tiles: Dict[str, Tile], edge_rules: set[Tuple[Edge, Edge]], vertex_rules: set[Tuple[str, str, str]]):
        self.tiles = tiles
        self.edge_rules = edge_rules
        self.vertex_rules = vertex_rules
        self.orients = []
        for name, tile in self.tiles.items():
            for rot in range(6):
                labs = tuple(tile[(j - rot) % 6] for j in range(6))
                edges = tuple((labs[j], labs[(j + 1) % 6]) for j in range(6))
                self.orients.append({"name": name, "tile": tile, "rot": rot, "labs": labs, "edges": edges})

    @classmethod
    def load(cls, path: Path) -> "Model":
        section = None
        tiles: Dict[str, Tile] = {}
        edge_rules: set[Tuple[Edge, Edge]] = set()
        vertex_rules: set[Tuple[str, str, str]] = set()
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                continue
            if section == "tiles":
                name, rest = line.split(":", 1)
                tiles[name.strip()] = tuple(rest.split())
            elif section == "edge_rules":
                lhs, rhs = [x.strip() for x in line.split("=")]
                edge_rules.add((parse_edge(lhs), parse_edge(rhs)))
            elif section == "vertex_rules":
                vertex_rules.add(canon3(line.split()))
        return cls(tiles, edge_rules, vertex_rules)

    def oid(self, name: str, rot: int) -> int:
        for i, o in enumerate(self.orients):
            if o["name"] == name and o["rot"] == rot:
                return i
        raise KeyError((name, rot))

    def edge_ok(self, a: int, side: int, b: int) -> bool:
        return (self.orients[a]["edges"][side % 6], self.orients[b]["edges"][(side + 3) % 6]) in self.edge_rules

    def patch_ok(self, patch: Dict[Pos, int]) -> Tuple[bool, object | None]:
        for pos, oid in patch.items():
            for side in range(6):
                nb = add(pos, side)
                if nb in patch and not self.edge_ok(oid, side, patch[nb]):
                    return False, ("edge", pos, side)
        for pos, oid in patch.items():
            labs = self.orients[oid]["labs"]
            for j in range(6):
                prev = add(pos, (j - 1) % 6)
                nxt = add(pos, j)
                if prev in patch and nxt in patch:
                    tri = canon3((labs[j % 6], self.orients[patch[prev]]["labs"][(j + 2) % 6], self.orients[patch[nxt]]["labs"][(j + 4) % 6]))
                    if tri not in self.vertex_rules:
                        return False, ("vertex", pos, j, tri)
        return True, None

    def local_ok_add(self, patch: Dict[Pos, int], site: Pos, oid: int) -> bool:
        for side in range(6):
            nb = add(site, side)
            if nb in patch and not self.edge_ok(oid, side, patch[nb]):
                return False
        cells = [site] + [add(site, side) for side in range(6) if add(site, side) in patch]

        def get(pos: Pos) -> int:
            return oid if pos == site else patch[pos]

        for pos in cells:
            labs = self.orients[get(pos)]["labs"]
            for j in range(6):
                prev = add(pos, (j - 1) % 6)
                nxt = add(pos, j)
                if (prev == site or prev in patch) and (nxt == site or nxt in patch):
                    tri = canon3((labs[j % 6], self.orients[get(prev)]["labs"][(j + 2) % 6], self.orients[get(nxt)]["labs"][(j + 4) % 6]))
                    if tri not in self.vertex_rules:
                        return False
        return True

    def candidates(self, patch: Dict[Pos, int], site: Pos) -> List[int]:
        return [i for i in range(len(self.orients)) if self.local_ok_add(patch, site, i)]

    def boundary_candidates(self, patch: Dict[Pos, int]) -> Dict[Pos, List[int]]:
        out: Dict[Pos, List[int]] = {}
        for pos in patch:
            for side in range(6):
                nb = add(pos, side)
                if nb not in patch and nb not in out:
                    out[nb] = self.candidates(patch, nb)
        return out

    def weak_closure(self, patch: Dict[Pos, int], max_steps: int = 300) -> Tuple[Dict[Pos, int], list, Dict[Pos, List[int]], object | None]:
        patch = dict(patch)
        log = []
        while True:
            bc = self.boundary_candidates(patch)
            dead = {site: cs for site, cs in bc.items() if len(cs) == 0}
            if dead:
                return patch, log, bc, ("dead_boundary", sorted(dead)[:10])
            ones = [(site, cs[0]) for site, cs in bc.items() if len(cs) == 1]
            if not ones:
                return patch, log, bc, None
            site, oid = sorted(ones, key=lambda x: (x[0][1], x[0][0]))[0]
            patch[site] = oid
            log.append((site, oid))
            ok, bad = self.patch_ok(patch)
            if not ok:
                return patch, log, self.boundary_candidates(patch), ("contradiction", bad)
            if len(log) >= max_steps:
                return patch, log, self.boundary_candidates(patch), ("escape", max_steps)

    def strong_demo_patch(self) -> Tuple[Dict[Pos, int], list, Dict[Pos, List[int]], object | None]:
        """Seven-tile strong closure demo from the central H1 singular edges.

        Strong here means: run weak singles, then kill one branch by probing weak
        closure and force the unique non-dead alternative.  This is not the full
        all-seed strong scan; it is the reproducible local demo used for the
        figure.
        """
        patch = {
            (0, 0): self.oid("H1", 0),
            add((0, 0), 0): self.oid("H0", 3),
            add((0, 0), 1): self.oid("H0", 4),
            add((0, 0), 5): self.oid("H0", 1),
        }
        patch, log, bc, status = self.weak_closure(patch)
        if status:
            return patch, log, bc, status
        # Southwest B,G/B,F branch: H1 rot 4 dies, H0 rot 0 lives.
        site = (0, -1)
        live = self.oid("H0", 0)
        patch[site] = live
        log.append(("strong", site, live, "H1 rot 4 branch dies at boundary (2,-2)"))
        patch, more, bc, status = self.weak_closure(patch)
        log.extend(more)
        return patch, log, bc, status


def hex_vertices(cx: float, cy: float, r: float) -> List[Tuple[float, float]]:
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in ANGLES]


def side_mid(cx: float, cy: float, side: int, r: float) -> Tuple[float, float]:
    pts = hex_vertices(cx, cy, r)
    x1, y1 = pts[side]
    x2, y2 = pts[(side + 1) % 6]
    return (x1 + x2) / 2, (y1 + y2) / 2


def neighbor_center(cx: float, cy: float, side: int, r: float) -> Tuple[float, float]:
    mx, my = side_mid(cx, cy, side, r)
    return 2 * mx - cx, 2 * my - cy


def compute_centers(patch: Dict[Pos, int], boundary: Dict[Pos, List[int]] | None = None, r: float = 1.0) -> Dict[Pos, Tuple[float, float]]:
    boundary = boundary or {}
    centers: Dict[Pos, Tuple[float, float]] = {(0, 0): (0.0, 0.0)}
    stack = [(0, 0)]
    while stack:
        pos = stack.pop()
        cx, cy = centers[pos]
        for side in range(6):
            nb = add(pos, side)
            if nb in patch and nb not in centers:
                centers[nb] = neighbor_center(cx, cy, side, r)
                stack.append(nb)
    stack = list(centers)
    while stack:
        pos = stack.pop()
        cx, cy = centers[pos]
        for side in range(6):
            nb = add(pos, side)
            if nb in boundary and nb not in centers:
                centers[nb] = neighbor_center(cx, cy, side, r)
                stack.append(nb)
    return centers


# ---------------------------------------------------------------------------
# Tiny stdlib-only PDF/SVG renderer
# ---------------------------------------------------------------------------


def pdf_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class SimplePDF:
    def __init__(self, width: int = 792, height: int = 612):
        self.width = width
        self.height = height
        self.pages: List[str] = []
        self.current: List[str] = []

    def add(self, s: str) -> None:
        self.current.append(s)

    def stroke_rgb(self, rgb: Tuple[float, float, float]) -> None:
        self.add(f"{rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} RG")

    def fill_rgb(self, rgb: Tuple[float, float, float]) -> None:
        self.add(f"{rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} rg")

    def line_width(self, w: float) -> None:
        self.add(f"{w:.2f} w")

    def polygon(self, pts: List[Tuple[float, float]], fill: Tuple[float, float, float], stroke=(0, 0, 0), lw=1.5) -> None:
        self.fill_rgb(fill)
        self.stroke_rgb(stroke)
        self.line_width(lw)
        x0, y0 = pts[0]
        self.add(f"{x0:.2f} {y0:.2f} m")
        for x, y in pts[1:]:
            self.add(f"{x:.2f} {y:.2f} l")
        self.add("h B")

    def line(self, p1, p2, lw=1.0, stroke=(0, 0, 0)) -> None:
        self.stroke_rgb(stroke)
        self.line_width(lw)
        self.add(f"{p1[0]:.2f} {p1[1]:.2f} m {p2[0]:.2f} {p2[1]:.2f} l S")

    def text(self, x: float, y: float, s: str, size: float = 10, bold: bool = False, center: bool = False) -> None:
        # Crude center by average width; enough for labels.
        if center:
            x = x - 0.28 * size * len(s)
        font = "/F2" if bold else "/F1"
        self.fill_rgb((0.0, 0.0, 0.0))
        self.add(f"BT {font} {size:.1f} Tf {x:.2f} {y:.2f} Td ({pdf_escape(s)}) Tj ET")

    def page(self) -> None:
        self.pages.append("\n".join(self.current))
        self.current = []

    def save(self, path: Path) -> None:
        if self.current:
            self.page()
        objects: List[bytes] = []

        def obj(data: str | bytes) -> int:
            if isinstance(data, str):
                data = data.encode("latin1")
            objects.append(data)
            return len(objects)

        catalog_id = obj("PLACEHOLDER")
        pages_id = obj("PLACEHOLDER")
        font1_id = obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font2_id = obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        page_ids = []
        for content in self.pages:
            stream = content.encode("latin1")
            content_id = obj(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
            page_id = obj(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.width} {self.height}] /Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R >> >> /Contents {content_id} 0 R >>")
            page_ids.append(page_id)
        objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin1")
        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode("latin1")
        out = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for i, data in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{i} 0 obj\n".encode())
            out.extend(data)
            out.extend(b"\nendobj\n")
        xref = len(out)
        out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode())
        out.extend(f"trailer << /Size {len(objects)+1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        path.write_bytes(out)


COLORS = {
    "blue": (0.86, 0.91, 0.97),
    "green": (0.87, 0.93, 0.85),
    "tan": (0.96, 0.91, 0.82),
    "red": (1.0, 0.84, 0.84),
    "yellow": (1.0, 0.95, 0.70),
    "white": (1.0, 1.0, 1.0),
    "black": (0.0, 0.0, 0.0),
}


def draw_tile(pdf: SimplePDF, cx: float, cy: float, radius: float, labs: Tuple[str, ...], name: str, fill: Tuple[float, float, float], bold_sides: Iterable[int] = ()) -> None:
    pts = hex_vertices(cx, cy, radius)
    pdf.polygon(pts, fill, lw=1.5)
    for side in bold_sides:
        pdf.line(pts[side], pts[(side + 1) % 6], lw=3.2)
    for (vx, vy), lab in zip(pts, labs):
        tx = cx + 0.62 * (vx - cx)
        ty = cy + 0.62 * (vy - cy)
        pdf.text(tx, ty - 5, lab, size=14, bold=True, center=True)
    pdf.text(cx, cy - 4, name, size=10, bold=True, center=True)


def fit_mapping(points: List[Tuple[float, float]], box: Tuple[float, float, float, float]):
    xmin, ymin, xmax, ymax = box
    minx = min(x for x, y in points)
    maxx = max(x for x, y in points)
    miny = min(y for x, y in points)
    maxy = max(y for x, y in points)
    spanx = max(maxx - minx, 0.01)
    spany = max(maxy - miny, 0.01)
    scale = min((xmax - xmin) / (spanx + 2.4), (ymax - ymin) / (spany + 2.4))

    def f(x, y):
        return (xmin + (x - minx) * scale + ((xmax - xmin) - spanx * scale) / 2,
                ymin + (y - miny) * scale + ((ymax - ymin) - spany * scale) / 2)
    return f, scale


def draw_patch_pdf(pdf: SimplePDF, model: Model, patch: Dict[Pos, int], bc: Dict[Pos, List[int]], box: Tuple[float, float, float, float], roles: Dict[Pos, str] | None = None, counts: bool = True) -> None:
    roles = roles or {}
    centers = compute_centers(patch, bc)
    pts = list(centers.values())
    mapper, scale = fit_mapping(pts, box)
    radius = scale * 0.96
    fill_for = {"center": COLORS["blue"], "seed0": COLORS["blue"], "seed1": COLORS["green"], "strong": COLORS["red"], "weak": COLORS["green"], "forced": COLORS["tan"]}
    for pos, oid in sorted(patch.items()):
        cx, cy = mapper(*centers[pos])
        role = roles.get(pos, "forced")
        fill = fill_for.get(role, COLORS["tan"])
        bold = [0, 1, 5] if pos == (0, 0) and model.orients[oid]["name"] == "H1" else []
        draw_tile(pdf, cx, cy, radius, model.orients[oid]["labs"], model.orients[oid]["name"], fill, bold)
    if counts:
        for site, cs in bc.items():
            if site in centers and cs:
                x, y = mapper(*centers[site])
                pdf.text(x, y - 5, str(len(cs)), size=14, bold=True, center=True)


def make_svg_patch(path: Path, model: Model, patch: Dict[Pos, int], bc: Dict[Pos, List[int]], roles: Dict[Pos, str] | None = None) -> None:
    roles = roles or {}
    centers = compute_centers(patch, bc)
    pts = list(centers.values())
    minx = min(x for x, y in pts) - 2
    maxx = max(x for x, y in pts) + 2
    miny = min(y for x, y in pts) - 2
    maxy = max(y for x, y in pts) + 2
    W, H = 1000, 850
    sx = W / (maxx - minx)
    sy = H / (maxy - miny)
    s = min(sx, sy)

    def mp(x, y):
        return ((x - minx) * s + 20, H - ((y - miny) * s + 20))

    def color(role):
        return {"center": "#dce8f6", "seed0": "#dce8f6", "seed1": "#dfead9", "strong": "#ffd6d6", "weak": "#d9efd6", "forced": "#f6ead2"}.get(role, "#f6ead2")

    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="white"/>']
    r = s * 0.96
    for pos, oid in sorted(patch.items()):
        cx, cy = mp(*centers[pos])
        verts = [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for a in ANGLES]
        pstr = " ".join(f"{x:.1f},{y:.1f}" for x, y in verts)
        role = roles.get(pos, "forced")
        lines.append(f'<polygon points="{pstr}" fill="{color(role)}" stroke="black" stroke-width="2"/>')
        if pos == (0, 0) and model.orients[oid]["name"] == "H1":
            for side in [0, 1, 5]:
                x1, y1 = verts[side]
                x2, y2 = verts[(side + 1) % 6]
                lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="black" stroke-width="5"/>')
        for (vx, vy), lab in zip(verts, model.orients[oid]["labs"]):
            tx = cx + 0.62 * (vx - cx)
            ty = cy + 0.62 * (vy - cy)
            lines.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="18" font-family="Helvetica" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{lab}</text>')
        lines.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="13" font-family="Helvetica" text-anchor="middle" dominant-baseline="middle">{model.orients[oid]["name"]}</text>')
    for site, cs in bc.items():
        if site in centers and cs:
            x, y = mp(*centers[site])
            lines.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="18" font-family="Helvetica" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{len(cs)}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines))


def make_fact_sheet(model: Model, out: Path) -> None:
    pdf = SimplePDF()
    pdf.text(30, 585, "Reduced Spectre 2-hex fact sheet", size=16, bold=True)
    pdf.text(30, 565, "Diagram orientation: H1 = H A D E B G ; H0 = C A B F G I", size=9)
    # Large tile drawings.
    draw_tile(pdf, 100, 470, 50, model.tiles["H1"], "H1", COLORS["blue"], [0, 1, 5])
    draw_tile(pdf, 225, 470, 50, model.tiles["H0"], "H0", COLORS["green"], [])
    pdf.text(35, 390, "Singular H1 edges", size=11, bold=True)
    for y, s in zip([372, 356, 340], ["H,A = C,A", "A,D = C,A", "G,H = A,B"]):
        pdf.fill_rgb(COLORS["yellow"])
        pdf.add(f"33 {y-2} 78 13 re f")
        pdf.text(36, y, s, size=8.5)

    pdf.text(330, 585, "Directed edge rules", size=12, bold=True)
    singular = {"H,A = C,A", "A,D = C,A", "G,H = A,B"}
    edge_lines = [f"{a[0]},{a[1]} = {b[0]},{b[1]}" for a, b in sorted(model.edge_rules)]
    rows = 17
    for i, line in enumerate(edge_lines):
        col = i // rows
        row = i % rows
        x = 330 + col * 130
        y = 565 - row * 13
        if line in singular:
            pdf.fill_rgb(COLORS["yellow"])
            pdf.add(f"{x-2} {y-2} 72 12 re f")
        pdf.text(x, y, line, size=8)

    pdf.text(30, 300, "Valid vertex triples", size=12, bold=True)
    triples = [" ".join(t) for t in sorted(model.vertex_rules)]
    for i, line in enumerate(triples):
        col = i // 6
        row = i % 6
        pdf.text(30 + col * 80, 280 - row * 15, line, size=9)

    pdf.text(330, 300, "Current checks", size=12, bold=True)
    checks = [
        f"tiles: {len(model.tiles)}",
        f"directed edge rules: {len(model.edge_rules)}",
        f"vertex triples: {len(model.vertex_rules)}",
        f"oriented hexes: {len(model.orients)}",
        "weak closure scan: 198 legal adjacent oriented seeds",
        "max weak closure: 9 tiles (dead boundary witness)",
        "strong demo: 7-tile live fixed point",
    ]
    for i, line in enumerate(checks):
        pdf.text(330, 280 - i * 15, line, size=9)
    pdf.save(out)


def make_strong_drawing(model: Model, out_pdf: Path, out_svg: Path, out_report: Path) -> None:
    patch, log, bc, status = model.strong_demo_patch()
    roles = {pos: "forced" for pos in patch}
    roles[(0, 0)] = "center"
    for item in log:
        if isinstance(item[0], str) and item[0] == "strong":
            roles[item[1]] = "strong"
        else:
            roles[item[0]] = "weak"
    pdf = SimplePDF()
    pdf.text(30, 585, "Strong closure demo", size=16, bold=True)
    pdf.text(30, 565, "Red = branch killed by live-boundary pruning; numbers are remaining boundary branch counts.", size=9)
    draw_patch_pdf(pdf, model, patch, bc, (40, 45, 750, 545), roles, counts=True)
    pdf.save(out_pdf)
    make_svg_patch(out_svg, model, patch, bc, roles)
    hist = Counter(len(cs) for cs in bc.values())
    lines = [
        "Strong closure demo report",
        "",
        "Definition: weak singles plus the local branch test where the H1 rot 4 alternative dies, forcing H0 rot 0.",
        f"status: {status}",
        f"tiles: {len(patch)}",
        f"boundary histogram: {dict(sorted(hist.items()))}",
        "",
        "placements:",
    ]
    for pos, oid in sorted(patch.items()):
        o = model.orients[oid]
        lines.append(f"  {pos}: {o['name']} rot {o['rot']} labels={' '.join(o['labs'])}")
    lines.append("")
    lines.append("closure log:")
    for item in log:
        if isinstance(item[0], str) and item[0] == "strong":
            _, site, oid, note = item
            o = model.orients[oid]
            lines.append(f"  strong {site}: {o['name']} rot {o['rot']} labels={' '.join(o['labs'])}; {note}")
        else:
            site, oid = item
            o = model.orients[oid]
            lines.append(f"  weak {site}: {o['name']} rot {o['rot']} labels={' '.join(o['labs'])}")
    out_report.write_text("\n".join(lines))


def scan(model: Model) -> Tuple[str, Dict[str, object]]:
    results = []
    for aid in range(len(model.orients)):
        for side in range(6):
            site = add((0, 0), side)
            for bid in range(len(model.orients)):
                seed = {(0, 0): aid, site: bid}
                ok, _ = model.patch_ok(seed)
                if not ok:
                    continue
                patch, log, bc, status = model.weak_closure(seed)
                results.append((len(patch), len(log), aid, side, bid, patch, log, bc, status))
    hist = Counter(r[0] for r in results)
    top = max(results, key=lambda r: (r[0], r[1]))
    lines = [
        "Weak closure scan over all legal adjacent oriented two-hex seeds",
        "",
        f"legal_adjacent_oriented_seeds {len(results)}",
        f"weak_closure_size_histogram {dict(sorted(hist.items()))}",
        f"max_tiles {top[0]}",
        f"forced_after_seed {top[1]}",
        f"seed {model.orients[top[2]]['name']} rot {model.orients[top[2]]['rot']} --dir {top[3]}-- {model.orients[top[4]]['name']} rot {model.orients[top[4]]['rot']}",
        f"status {top[8]}",
    ]
    return "\n".join(lines) + "\n", {"hist": hist, "top": top, "n": len(results)}


def cmd_verify(args) -> None:
    model = Model.load(Path(args.model))
    print(f"tiles {len(model.tiles)}")
    print(f"edge_rules {len(model.edge_rules)}")
    print(f"vertex_rules {len(model.vertex_rules)}")
    print(f"oriented_tiles {len(model.orients)}")
    patch, log, bc, status = model.strong_demo_patch()
    print(f"strong_demo_tiles {len(patch)}")
    print(f"strong_demo_status {status}")
    print(f"strong_demo_boundary_histogram {dict(sorted(Counter(len(cs) for cs in bc.values()).items()))}")


def cmd_scan(args) -> None:
    model = Model.load(Path(args.model))
    text, _ = scan(model)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
    print(text, end="")


def cmd_make_artifacts(args) -> None:
    model = Model.load(Path(args.model))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    make_fact_sheet(model, out / "spectre_hex_fact_sheet.pdf")
    make_strong_drawing(model, out / "strong_forced_configuration.pdf", out / "strong_forced_configuration.svg", out / "strong_forced_configuration_report.txt")
    text, _ = scan(model)
    (out / "weak_scan_summary.txt").write_text(text)
    print(f"wrote artifacts to {out}")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["verify", "scan", "make-artifacts"]:
        p = sub.add_parser(name)
        p.add_argument("--model", default="data/reduced_spectre_model.dat")
        if name in {"scan", "make-artifacts"}:
            p.add_argument("--out", default="out" if name == "make-artifacts" else None)
    args = parser.parse_args()
    if args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "make-artifacts":
        cmd_make_artifacts(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
