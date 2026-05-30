#!/usr/bin/env python3
"""Render triangle periodic certificate records into SVG panels and a PDF report.

This renderer intentionally uses only the Python standard library.  The SAT
search has one external dependency (python-sat); PDF/SVG generation should not
require installing an unrelated graphics stack.
"""
from __future__ import annotations

import argparse
import html
import math
import textwrap
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Point = Tuple[float, float]
PAGE_W, PAGE_H = 792.0, 612.0  # US letter landscape, points
PANEL_W, PANEL_H = 420.0, 290.0
EDGE_COLOR = "#202020"
ABC_FILL = "#e8f1ff"
DEF_FILL = "#fff1e3"
FRAME_COLOR = "#666666"
TEXT_COLOR = "#111111"


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float
    fill: str
    stroke: str
    stroke_width: float = 1.0


@dataclass(frozen=True)
class Poly:
    points: Tuple[Point, ...]
    fill: str | None
    stroke: str
    stroke_width: float
    dash: Tuple[float, ...] = ()


@dataclass(frozen=True)
class Text:
    x: float
    y: float
    value: str
    size: float
    bold: bool = False
    anchor: str = "start"
    fill: str = TEXT_COLOR


Op = Rect | Poly | Text


def parse_records(path: Path) -> Tuple[dict, List[dict]]:
    meta: dict = {}
    records: List[dict] = []
    current = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("meta "):
                for piece in line.split()[1:]:
                    key, value = piece.split("=", 1)
                    meta[key] = value
            elif line.startswith("record "):
                current = {"index": int(line.split()[1]), "cells": []}
            elif line == "end":
                assert current is not None
                records.append(current)
                current = None
            else:
                assert current is not None, f"unexpected line outside record: {line}"
                key, rest = line.split(" ", 1)
                if key == "mask":
                    current["mask"] = rest
                elif key == "bits":
                    current["bits"] = int(rest)
                elif key == "torus":
                    width, height = rest.split()
                    current["width"] = int(width)
                    current["height"] = int(height)
                elif key == "rules":
                    current["rules"] = rest
                elif key == "cells":
                    current["cell_count"] = int(rest)
                elif key == "state":
                    orient, i, j, *edges = rest.split()
                    current["cells"].append({
                        "orient": orient,
                        "i": int(i),
                        "j": int(j),
                        "edges": tuple(edges),
                    })
                else:
                    raise ValueError(f"unknown key {key}")
    return meta, records


def lattice_to_xy(vertex: Tuple[int, int]) -> Point:
    a, b = vertex
    return (a + 0.5 * b, (math.sqrt(3) / 2.0) * b)


def tri_vertices(cell: dict) -> List[Tuple[int, int]]:
    orient, i, j = cell["orient"], cell["i"], cell["j"]
    if orient == "U":
        return [(i, j), (i + 1, j), (i, j + 1)]
    return [(i + 1, j), (i + 1, j + 1), (i, j + 1)]


def infer_vertex_labels(edges: Tuple[str, str, str]) -> Tuple[str, str, str]:
    vertices = sorted(set("".join(edges)))
    for v0, v1, v2 in permutations(vertices):
        if ({v0, v1} == set(edges[0]) and
                {v1, v2} == set(edges[1]) and
                {v2, v0} == set(edges[2])):
            return (v0, v1, v2)
    raise ValueError(f"could not infer vertex labels for edges={edges}")


def poly_bounds(polygons: Sequence[Sequence[Point]]) -> Tuple[float, float, float, float]:
    xs = [point[0] for polygon in polygons for point in polygon]
    ys = [point[1] for polygon in polygons for point in polygon]
    return min(xs), min(ys), max(xs), max(ys)


def panel_ops(rec: dict) -> List[Op]:
    ops: List[Op] = [Rect(0, 0, PANEL_W, PANEL_H, "#ffffff", "#cccccc", 1)]
    title = f"#{rec['index']:02d}  {rec['mask']}  {rec['width']}x{rec['height']}  bits={rec['bits']}"
    ops.append(Text(12, 18, title, 14, bold=True))
    rule_text = rec["rules"] if rec["rules"] != "-" else "(none)"
    y = 36
    for line in textwrap.wrap("AB=DE; " + rule_text, width=42)[:3]:
        ops.append(Text(12, y, line, 11))
        y += 13

    image_left, image_top = 10.0, 80.0
    image_right, image_bottom = PANEL_W - 10.0, PANEL_H - 10.0
    image_w = image_right - image_left
    image_h = image_bottom - image_top

    cell_polys: List[Tuple[dict, List[Point], Point]] = []
    for cell in rec["cells"]:
        vertices = [lattice_to_xy(v) for v in tri_vertices(cell)]
        centroid = (sum(x for x, _ in vertices) / 3.0,
                    sum(y for _, y in vertices) / 3.0)
        cell_polys.append((cell, vertices, centroid))

    frame = [
        lattice_to_xy((0, 0)),
        lattice_to_xy((rec["width"], 0)),
        lattice_to_xy((rec["width"], rec["height"])),
        lattice_to_xy((0, rec["height"])),
    ]
    minx, miny, maxx, maxy = poly_bounds([vertices for _, vertices, _ in cell_polys] + [frame])
    pad = 0.35
    minx -= pad
    miny -= pad
    maxx += pad
    maxy += pad
    scale = min(image_w / (maxx - minx), image_h / (maxy - miny))
    tx = image_left + (image_w - scale * (maxx - minx)) / 2.0
    ty = image_top + (image_h - scale * (maxy - miny)) / 2.0

    def map_point(point: Point) -> Point:
        return (tx + scale * (point[0] - minx),
                ty + scale * (maxy - point[1]))

    ops.append(Poly(tuple(map_point(p) for p in frame), None, FRAME_COLOR, 1.4, (5.0, 4.0)))
    for cell, vertices, centroid in cell_polys:
        is_abc = any(edge == "AB" for edge in cell["edges"])
        fill = ABC_FILL if is_abc else DEF_FILL
        ops.append(Poly(tuple(map_point(p) for p in vertices), fill, EDGE_COLOR, 1.4))
        labels = infer_vertex_labels(cell["edges"])
        for k, label in enumerate(labels):
            vx, vy = vertices[k]
            lx = 0.68 * vx + 0.32 * centroid[0]
            ly = 0.68 * vy + 0.32 * centroid[1]
            px, py = map_point((lx, ly))
            ops.append(Text(px, py + 5, label, 15, bold=True, anchor="middle"))
    return ops


def chunked_layout(records: List[dict]) -> List[Tuple[str, List[dict], int, int]]:
    groups: Dict[Tuple[int, int], List[dict]] = {}
    for rec in records:
        groups.setdefault((rec["width"], rec["height"]), []).append(rec)
    for key in groups:
        groups[key].sort(key=lambda r: (r["bits"], r["mask"]))

    layout: List[Tuple[str, List[dict], int, int]] = []
    compact = groups.get((1, 1), []) + groups.get((2, 2), [])
    if compact:
        layout.append(("1x1 and 2x2 witnesses", compact, 5, 2))
    if (3, 3) in groups:
        layout.append(("3x3 witnesses", groups[(3, 3)], 2, 2))
    if (1, 2) in groups:
        layout.append(("1x2 witnesses", groups[(1, 2)], 6, 3))
    if (1, 3) in groups:
        layout.append(("1x3 witnesses", groups[(1, 3)], 6, 3))
    used = {(1, 1), (2, 2), (3, 3), (1, 2), (1, 3)}
    for key in sorted(groups):
        if key not in used:
            recs = groups[key]
            cols = min(4, max(1, math.ceil(math.sqrt(len(recs)))))
            rows = math.ceil(len(recs) / cols)
            layout.append((f"{key[0]}x{key[1]} witnesses", recs, cols, rows))
    return layout


def color_rgb(hex_color: str) -> Tuple[float, float, float]:
    value = hex_color.removeprefix("#")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def escaped_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def estimated_text_width(value: str, size: float, bold: bool) -> float:
    return size * (0.57 if bold else 0.52) * len(value)


def transformed_ops(ops: Iterable[Op], x: float, y: float, scale: float) -> List[Op]:
    result: List[Op] = []
    for op in ops:
        if isinstance(op, Rect):
            result.append(Rect(x + scale * op.x, y + scale * op.y, scale * op.w,
                               scale * op.h, op.fill, op.stroke, scale * op.stroke_width))
        elif isinstance(op, Poly):
            result.append(Poly(tuple((x + scale * px, y + scale * py) for px, py in op.points),
                               op.fill, op.stroke, scale * op.stroke_width,
                               tuple(scale * d for d in op.dash)))
        else:
            result.append(Text(x + scale * op.x, y + scale * op.y, op.value,
                               scale * op.size, op.bold, op.anchor, op.fill))
    return result


def svg_for_ops(ops: Iterable[Op], width: float, height: float) -> str:
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}">']
    for op in ops:
        if isinstance(op, Rect):
            lines.append(f'<rect x="{op.x:g}" y="{op.y:g}" width="{op.w:g}" height="{op.h:g}" fill="{op.fill}" stroke="{op.stroke}" stroke-width="{op.stroke_width:g}"/>')
        elif isinstance(op, Poly):
            points = " ".join(f"{x:g},{y:g}" for x, y in op.points)
            fill = op.fill if op.fill else "none"
            dash = f' stroke-dasharray="{",".join(f"{d:g}" for d in op.dash)}"' if op.dash else ""
            lines.append(f'<polygon points="{points}" fill="{fill}" stroke="{op.stroke}" stroke-width="{op.stroke_width:g}"{dash}/>')
        else:
            anchor = "middle" if op.anchor == "middle" else "start"
            weight = "bold" if op.bold else "normal"
            value = html.escape(op.value)
            lines.append(f'<text x="{op.x:g}" y="{op.y:g}" text-anchor="{anchor}" font-size="{op.size:g}px" font-family="Helvetica,Arial,sans-serif" font-weight="{weight}" fill="{op.fill}">{value}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def pdf_stream_for_ops(ops: Iterable[Op]) -> bytes:
    commands: List[str] = []
    for op in ops:
        if isinstance(op, Rect):
            fr, fg, fb = color_rgb(op.fill)
            sr, sg, sb = color_rgb(op.stroke)
            y_pdf = PAGE_H - op.y - op.h
            commands.append(f"q {fr:.4f} {fg:.4f} {fb:.4f} rg {sr:.4f} {sg:.4f} {sb:.4f} RG {op.stroke_width:.3f} w {op.x:.3f} {y_pdf:.3f} {op.w:.3f} {op.h:.3f} re B Q")
        elif isinstance(op, Poly):
            sr, sg, sb = color_rgb(op.stroke)
            dash = ("[" + " ".join(f"{d:.3f}" for d in op.dash) + "] 0 d") if op.dash else "[] 0 d"
            first_x, first_y = op.points[0]
            path = [f"{first_x:.3f} {PAGE_H - first_y:.3f} m"]
            for px, py in op.points[1:]:
                path.append(f"{px:.3f} {PAGE_H - py:.3f} l")
            path.append("h")
            if op.fill:
                fr, fg, fb = color_rgb(op.fill)
                commands.append(f"q {fr:.4f} {fg:.4f} {fb:.4f} rg {sr:.4f} {sg:.4f} {sb:.4f} RG {op.stroke_width:.3f} w {dash} {' '.join(path)} B Q")
            else:
                commands.append(f"q {sr:.4f} {sg:.4f} {sb:.4f} RG {op.stroke_width:.3f} w {dash} {' '.join(path)} S Q")
        else:
            r, g, b = color_rgb(op.fill)
            font = "F2" if op.bold else "F1"
            x = op.x
            if op.anchor == "middle":
                x -= estimated_text_width(op.value, op.size, op.bold) / 2.0
            y = PAGE_H - op.y
            value = escaped_pdf_text(op.value)
            commands.append(f"BT /{font} {op.size:.3f} Tf {r:.4f} {g:.4f} {b:.4f} rg {x:.3f} {y:.3f} Td ({value}) Tj ET")
    return ("\n".join(commands) + "\n").encode("latin-1", "replace")


def write_pdf(page_ops: Sequence[Sequence[Op]], output: Path) -> None:
    objects: List[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    catalog_id = add(b"")
    pages_id = add(b"")
    regular_font_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold_font_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids: List[int] = []
    for ops in page_ops:
        stream = pdf_stream_for_ops(ops)
        content_id = add(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_W:g} {PAGE_H:g}] ".encode("ascii") +
            f"/Resources << /Font << /F1 {regular_font_id} 0 R /F2 {bold_font_id} 0 R >> >> ".encode("ascii") +
            f"/Contents {content_id} 0 R >>".encode("ascii")
        )
        page_ids.append(page_id)
    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")

    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode("ascii"))
        data.extend(obj)
        data.extend(b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    output.write_bytes(data)


def make_panel_svg(rec: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg_for_ops(panel_ops(rec), PANEL_W, PANEL_H), encoding="utf-8")


def assemble_pdf(records: List[dict], output: Path, meta: dict) -> None:
    pages: List[List[Op]] = []
    margin, title_h, gap = 16.0, 28.0, 8.0
    for page_number, (title, recs, cols, rows) in enumerate(chunked_layout(records), start=1):
        ops: List[Op] = [Text(margin, margin, f"Triangle periodic certificates - {title}", 16, bold=True)]
        summary = f"mandatory anchor AB=DE; periodic_area={meta.get('periodic_area', '?')}; solver={meta.get('solver', '?')}; page {page_number}"
        ops.append(Text(margin, margin + 13, summary, 10))
        usable_w = PAGE_W - 2 * margin
        usable_h = PAGE_H - 2 * margin - title_h
        cell_w = (usable_w - (cols - 1) * gap) / cols
        cell_h = (usable_h - (rows - 1) * gap) / rows
        scale = min(cell_w / PANEL_W, cell_h / PANEL_H)
        for index, rec in enumerate(recs):
            row, col = divmod(index, cols)
            x0 = margin + col * (cell_w + gap) + (cell_w - PANEL_W * scale) / 2.0
            y0 = margin + title_h + row * (cell_h + gap) + (cell_h - PANEL_H * scale) / 2.0
            ops.extend(transformed_ops(panel_ops(rec), x0, y0, scale))
        pages.append(ops)
    write_pdf(pages, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", help="record text file from triangle_export_periodic_records.py")
    parser.add_argument("--svg-dir", required=True, help="directory for per-certificate SVG panels")
    parser.add_argument("--pdf", required=True, help="output PDF path")
    args = parser.parse_args()

    meta, records = parse_records(Path(args.records))
    svg_dir = Path(args.svg_dir)
    for rec in records:
        make_panel_svg(rec, svg_dir / f"cert_{rec['index']:02d}_{rec['mask']}_{rec['width']}x{rec['height']}.svg")
    assemble_pdf(records, Path(args.pdf), meta)
    print(f"wrote {len(records)} SVG panels to {svg_dir}")
    print(f"wrote PDF report to {args.pdf}")


if __name__ == "__main__":
    main()
