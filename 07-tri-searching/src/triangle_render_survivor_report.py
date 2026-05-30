#!/usr/bin/env python3
"""Render survivor configuration records into SVG panels and a PDF report."""
from __future__ import annotations

import argparse
import math
import textwrap
from pathlib import Path
from typing import List, Tuple

from triangle_render_periodic_report import (
    ABC_FILL,
    DEF_FILL,
    EDGE_COLOR,
    PANEL_H,
    PANEL_W,
    PAGE_H,
    PAGE_W,
    Poly,
    Rect,
    StrokePath,
    Text,
    distinguished_notch,
    lattice_to_xy,
    poly_bounds,
    transformed_ops,
    tri_vertices,
    svg_for_ops,
    write_pdf,
)


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
                elif key == "depth":
                    current["depth"] = int(rest)
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


def panel_ops(rec: dict) -> List[Rect | Poly | StrokePath | Text]:
    ops: List[Rect | Poly | StrokePath | Text] = [Rect(0, 0, PANEL_W, PANEL_H, "#ffffff", "#cccccc", 1)]
    title = f"#{rec['index']:02d}  {rec['mask']}  bits={rec['bits']}  depth={rec['depth']}"
    ops.append(Text(12, 18, title, 14, bold=True))
    y = 36
    for line in textwrap.wrap(rec["rules"] if rec["rules"] != "-" else "(none)", width=48)[:3]:
        ops.append(Text(12, y, line, 11))
        y += 13

    image_left, image_top = 10.0, 72.0
    image_right, image_bottom = PANEL_W - 10.0, PANEL_H - 10.0
    image_w = image_right - image_left
    image_h = image_bottom - image_top

    cell_polys = []
    for cell in rec["cells"]:
        vertices = [lattice_to_xy(v) for v in tri_vertices(cell)]
        cell_polys.append((cell, vertices))

    minx, miny, maxx, maxy = poly_bounds([vertices for _, vertices in cell_polys])
    pad = 0.35
    minx -= pad
    miny -= pad
    maxx += pad
    maxy += pad
    scale = min(image_w / (maxx - minx), image_h / (maxy - miny))
    tx = image_left + (image_w - scale * (maxx - minx)) / 2.0
    ty = image_top + (image_h - scale * (maxy - miny)) / 2.0

    def map_point(point):
        return (tx + scale * (point[0] - minx), ty + scale * (maxy - point[1]))

    for cell, vertices in cell_polys:
        is_abc = any(edge == "AB" for edge in cell["edges"])
        fill = ABC_FILL if is_abc else DEF_FILL
        stroke_width = 0.55 if len(rec["cells"]) > 200 else 0.8
        ops.append(Poly(tuple(map_point(p) for p in vertices), fill, EDGE_COLOR, stroke_width))
        notch = distinguished_notch(vertices, cell["edges"])
        ops.append(Poly(tuple(map_point(p) for p in notch), EDGE_COLOR, EDGE_COLOR, max(0.45, 0.7 * stroke_width)))
    return ops


def make_panel_svg(rec: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg_for_ops(panel_ops(rec), PANEL_W, PANEL_H), encoding="utf-8")


def assemble_pdf(records: List[dict], output: Path, meta: dict) -> None:
    pages: List[List[Rect | Poly | StrokePath | Text]] = []
    margin, title_h, gap = 16.0, 28.0, 8.0
    cols, rows = 2, 2
    per_page = cols * rows
    total_pages = math.ceil(len(records) / per_page)
    for page_number in range(total_pages):
        start = page_number * per_page
        recs = records[start:start + per_page]
        ops: List[Rect | Poly | StrokePath | Text] = [Text(margin, margin, "Triangle survivor configurations", 16, bold=True)]
        summary = (
            f"family={meta.get('family','anchored')}; periodic_area={meta.get('periodic_area','?')}; "
            f"completion_depth={meta.get('completion_depth','?')}; solver={meta.get('solver','?')}; "
            f"survivors={meta.get('count','?')}; page {page_number + 1}/{total_pages}"
        )
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
    parser.add_argument("records", help="record text file from triangle_export_survivor_records.py")
    parser.add_argument("--svg-dir", required=True, help="directory for per-survivor SVG panels")
    parser.add_argument("--pdf", required=True, help="output PDF path")
    args = parser.parse_args()

    meta, records = parse_records(Path(args.records))
    svg_dir = Path(args.svg_dir)
    for rec in records:
        make_panel_svg(rec, svg_dir / f"survivor_{rec['index']:02d}_{rec['mask']}.svg")
    assemble_pdf(records, Path(args.pdf), meta)
    print(f"wrote {len(records)} SVG panels to {svg_dir}")
    print(f"wrote PDF report to {args.pdf}")


if __name__ == "__main__":
    main()
