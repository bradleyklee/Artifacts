#!/usr/bin/env python3
"""Data-driven SVG renderer for the checked N=18 and N=45 disk witnesses.

It imports the exact checker and refuses to render a figure until the relevant
input has passed the same no-missing/no-extra membership test used by make check.
The SVG geometry itself is derived solely from the checked records.
"""
from __future__ import annotations

import argparse
import html
import json
import math
from fractions import Fraction
from pathlib import Path

from verify import N18Record, N45Record, fmt, verify_n18, verify_n45


COLORS = {
    "grid": "#d8dee9",
    "axis": "#64748b",
    "text": "#18212f",
    "muted": "#475569",
    "cell_fill": "#d9eaff",
    "cell_stroke": "#3066a4",
    "circle": "#dc2626",
    "center": "#dc2626",
    "inside": "#0f766e",
    "boundary": "#b45309",
    "outside": "#9ca3af",
    "bar": "#245b98",
    "site": "#1d4e89",
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def svg_root(width: int, height: int, body: list[str], title: str) -> str:
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <desc id="desc">Vector plot generated from exact rational circle-lattice witness data.</desc>',
        '  <rect width="100%" height="100%" fill="white"/>',
        *body,
        '</svg>',
        '',
    ])


def text(x: float, y: float, value: str, size: float = 14, weight: str = "normal", fill: str | None = None, anchor: str = "start") -> str:
    color = fill or COLORS["text"]
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size:.1f}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{esc(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 1, opacity: float = 1.0, dash: str | None = None) -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{stroke}" stroke-width="{width:.3f}" opacity="{opacity:.3f}"{extra}/>'


def circle(cx: float, cy: float, r: float, stroke: str | None = None, fill: str = "none", width: float = 1, opacity: float = 1.0) -> str:
    st = f' stroke="{stroke}" stroke-width="{width:.3f}"' if stroke else ""
    return f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{fill}"{st} opacity="{opacity:.3f}"/>'


def rect(x: float, y: float, w: float, h: float, fill: str = "none", stroke: str | None = None, width: float = 1, opacity: float = 1.0) -> str:
    st = f' stroke="{stroke}" stroke-width="{width:.3f}"' if stroke else ""
    return f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill}"{st} opacity="{opacity:.3f}"/>'


def panel_mapper(box: tuple[int, int, int, int], px: float, py: float, pw: float, ph: float):
    x0, x1, y0, y1 = box
    # Integer points x0..x1 and y0..y1 occupy the full lattice extent.  The
    # extra half-cell margin keeps boundary dots from clipping against the frame.
    vx0, vx1 = x0 - 0.45, x1 + 0.45
    vy0, vy1 = y0 - 0.45, y1 + 0.45
    sx = pw / (vx1 - vx0)
    sy = ph / (vy1 - vy0)
    s = min(sx, sy)
    used_w = (vx1 - vx0) * s
    used_h = (vy1 - vy0) * s
    ox = px + (pw - used_w) / 2 - vx0 * s
    oy = py + (ph - used_h) / 2 + vy1 * s

    def mp(x: float | Fraction, y: float | Fraction) -> tuple[float, float]:
        return ox + float(x) * s, oy - float(y) * s

    return mp, s, (px + (pw - used_w) / 2, py + (ph - used_h) / 2, used_w, used_h)


def add_lattice(body: list[str], box: tuple[int, int, int, int], mp, s: float, plot_rect: tuple[float, float, float, float]) -> None:
    x0, x1, y0, y1 = box
    lx, ly, lw, lh = plot_rect
    body.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#cbd5e1", width=1))
    for x in range(x0, x1 + 1):
        xa, ya = mp(x, y0)
        xb, yb = mp(x, y1)
        body.append(line(xa, ya, xb, yb, COLORS["grid"], 0.75))
        body.append(text(xa, ly + lh + 17, str(x), 11, fill=COLORS["muted"], anchor="middle"))
    for y in range(y0, y1 + 1):
        xa, ya = mp(x0, y)
        xb, yb = mp(x1, y)
        body.append(line(xa, ya, xb, yb, COLORS["grid"], 0.75))
        body.append(text(lx - 9, ya + 4, str(y), 11, fill=COLORS["muted"], anchor="end"))


def panel_n18(body: list[str], rec: N18Record, x: float, y: float, w: float, h: float) -> None:
    body.append(rect(x, y, w, h, fill="#ffffff", stroke="#aab7c4", width=1.4))
    body.append(text(x + 16, y + 27, f"{rec.ident} — 18 contained unit squares", 18, "bold"))
    body.append(text(x + 16, y + 48, f"C = ({fmt(rec.center[0])}, {fmt(rec.center[1])}),   r² = {fmt(rec.r2)}", 12.5, fill=COLORS["muted"]))
    body.append(text(x + 16, y + 66, f"disk vertices = {len(rec.disk_vertices)} = cell vertices; induced cells = {len(rec.induced_cells)}", 12, fill=COLORS["muted"]))
    plot_x, plot_y, plot_w, plot_h = x + 46, y + 82, w - 64, h - 155
    mp, scale, pr = panel_mapper(rec.box, plot_x, plot_y, plot_w, plot_h)
    add_lattice(body, rec.box, mp, scale, pr)
    # Contained cells are lower-left unit-square coordinates in the standard grid.
    for i, j in sorted(rec.cells):
        xa, ya = mp(i, j + 1)
        xb, yb = mp(i + 1, j)
        body.append(rect(min(xa, xb), min(ya, yb), abs(xb - xa), abs(yb - ya), COLORS["cell_fill"], COLORS["cell_stroke"], 1.25, 0.94))
    cx, cy = mp(rec.center[0], rec.center[1])
    cr = math.sqrt(float(rec.r2)) * scale
    body.append(circle(cx, cy, cr, COLORS["circle"], "none", 2.25))
    x0, x1, y0, y1 = rec.box
    for gx in range(x0, x1 + 1):
        for gy in range(y0, y1 + 1):
            point = (gx, gy)
            px, py = mp(gx, gy)
            if point in rec.disk_vertices:
                boundary = (Fraction(gx) - rec.center[0]) ** 2 + (Fraction(gy) - rec.center[1]) ** 2 == rec.r2
                color = COLORS["boundary"] if boundary else COLORS["inside"]
                body.append(circle(px, py, 3.7, color, color, 0.8))
            else:
                body.append(circle(px, py, 2.1, COLORS["outside"], COLORS["outside"], 0.5, 0.72))
    body.append(circle(cx, cy, 4.1, COLORS["center"], COLORS["center"], 1))
    body.append(text(x + 16, y + h - 19, f"strict / boundary vertices: {rec.strict_vertices} / {rec.boundary_vertices}   •   missing = extra = 0", 12, fill=COLORS["muted"]))


def panel_n45(body: list[str], rec: N45Record, x: float, y: float, w: float, h: float) -> None:
    body.append(rect(x, y, w, h, fill="#ffffff", stroke="#aab7c4", width=1.4))
    body.append(text(x + 16, y + 27, f"{rec.ident} — 45 lattice sites / polystick", 16.5, "bold"))
    body.append(text(x + 16, y + 46, f"C = ({fmt(rec.center[0])}, {fmt(rec.center[1])}),   r² = {fmt(rec.r2)}", 11.5, fill=COLORS["muted"]))
    body.append(text(x + 16, y + 63, "D(C,r) ∩ Z² = listed sites = 45; bars join unit-adjacent sites only", 11.3, fill=COLORS["muted"]))
    plot_x, plot_y, plot_w, plot_h = x + 45, y + 78, w - 61, h - 147
    mp, scale, pr = panel_mapper(rec.box, plot_x, plot_y, plot_w, plot_h)
    add_lattice(body, rec.box, mp, scale, pr)
    cx, cy = mp(rec.center[0], rec.center[1])
    cr = math.sqrt(float(rec.r2)) * scale
    body.append(circle(cx, cy, cr, COLORS["circle"], "none", 2.1))
    # Polystick bars: no unit squares are drawn in this model.
    for sx, sy in sorted(rec.sites):
        for tx, ty in ((sx + 1, sy), (sx, sy + 1)):
            if (tx, ty) in rec.sites:
                x1, y1 = mp(sx, sy)
                x2, y2 = mp(tx, ty)
                body.append(line(x1, y1, x2, y2, COLORS["bar"], 2.2, 0.92))
    x0, x1, y0, y1 = rec.box
    for gx in range(x0, x1 + 1):
        for gy in range(y0, y1 + 1):
            point = (gx, gy)
            px, py = mp(gx, gy)
            if point in rec.sites:
                boundary = (Fraction(gx) - rec.center[0]) ** 2 + (Fraction(gy) - rec.center[1]) ** 2 == rec.r2
                color = COLORS["boundary"] if boundary else COLORS["site"]
                body.append(circle(px, py, 3.5, color, color, 0.7))
            else:
                body.append(circle(px, py, 1.9, COLORS["outside"], COLORS["outside"], 0.4, 0.65))
    body.append(circle(cx, cy, 3.9, COLORS["center"], COLORS["center"], 1))
    body.append(text(x + 16, y + h - 18, f"strict / boundary sites: {rec.strict_sites} / {rec.boundary_sites}   •   missing = extra = 0", 11.4, fill=COLORS["muted"]))


def n18_sheet(records: list[N18Record]) -> str:
    width, height = 1260, 1320
    margin, header, gap = 46, 132, 26
    panel_w = (width - 2 * margin - gap) / 2
    panel_h = (height - header - margin * 1.25 - gap) / 2
    body = [
        text(margin, 45, "N=18 — disk-bounded unit-square configurations", 28, "bold"),
        text(margin, 70, "Standard lower-left-corner grid. Blue squares are the induced 18-cell polyominoes; all grid vertices in or on each closed disk are plotted.", 14, fill=COLORS["muted"]),
        text(margin, 94, "green = strict disk vertex   •   amber = boundary vertex   •   gray = ambient lattice vertex   •   red = circle / center", 13, fill=COLORS["muted"]),
    ]
    for k, rec in enumerate(records):
        col, row = k % 2, k // 2
        x = margin + col * (panel_w + gap)
        y = header + row * (panel_h + gap)
        panel_n18(body, rec, x, y, panel_w, panel_h)
    body.append(text(width / 2, height - 20, "Exact check: disk grid-vertex set equals the polyomino's cell-vertex union; induced unit-cell set equals the 18 listed cells.", 13, fill=COLORS["muted"], anchor="middle"))
    return svg_root(width, height, body, "N=18 disk-bounded unit-square configurations")


def n45_sheet(records: list[N45Record]) -> str:
    width, height = 1510, 1980
    margin, header, gap = 42, 130, 22
    panel_w = (width - 2 * margin - 2 * gap) / 3
    panel_h = (height - header - margin - 3 * gap) / 4
    body = [
        text(margin, 43, "N=45 — disk-bounded lattice-site / polystick configurations", 28, "bold"),
        text(margin, 68, "Physical integer lattice Z². Blue dots are selected sites; blue bars join horizontal/vertical neighbors only. No filled-square semantics are used.", 14, fill=COLORS["muted"]),
        text(margin, 92, "blue = strict selected site   •   amber = boundary selected site   •   gray = ambient lattice site   •   red = circle / center", 13, fill=COLORS["muted"]),
    ]
    for k, rec in enumerate(records):
        col, row = k % 3, k // 3
        x = margin + col * (panel_w + gap)
        y = header + row * (panel_h + gap)
        panel_n45(body, rec, x, y, panel_w, panel_h)
    body.append(text(width / 2, height - 18, "Exact check in every panel: D(C,r) ∩ Z² is exactly the displayed 45-site set (no missing sites, no extras).", 13, fill=COLORS["muted"], anchor="middle"))
    return svg_root(width, height, body, "N=45 disk-bounded lattice-site / polystick configurations")


def single_n18(rec: N18Record) -> str:
    body: list[str] = []
    panel_n18(body, rec, 30, 30, 720, 720)
    return svg_root(780, 780, body, f"N=18 {rec.ident}")


def single_n45(rec: N45Record) -> str:
    body: list[str] = []
    panel_n45(body, rec, 30, 30, 620, 620)
    return svg_root(680, 680, body, f"N=45 {rec.ident}")


def index_html(n18: list[N18Record], n45: list[N45Record]) -> str:
    links18 = "\n".join(f'<li><a href="n18_{r.ident}.svg">{r.ident}</a></li>' for r in n18)
    links45 = "\n".join(f'<li><a href="n45_{r.ident}.svg">{r.ident}</a></li>' for r in n45)
    return f"""<!doctype html>
<html><head><meta charset=\"utf-8\"><title>Circle lattice MWE plots</title>
<style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:30px auto;line-height:1.4}}img{{max-width:100%;border:1px solid #cbd5e1}}section{{margin-bottom:35px}}</style></head>
<body><h1>Circle-lattice minimal working example</h1>
<section><h2>N=18 unit-square / polyomino</h2><img src=\"n18_contact_sheet.svg\" alt=\"N=18 contact sheet\"><ul>{links18}</ul></section>
<section><h2>N=45 lattice-site / polystick</h2><img src=\"n45_contact_sheet.svg\" alt=\"N=45 contact sheet\"><ul>{links45}</ul></section>
</body></html>\n"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n18", type=Path, required=True)
    p.add_argument("--n45", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    n18 = verify_n18(json.loads(args.n18.read_text()))
    n45 = verify_n45(json.loads(args.n45.read_text()))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "n18_contact_sheet.svg").write_text(n18_sheet(n18))
    (args.out / "n45_contact_sheet.svg").write_text(n45_sheet(n45))
    for rec in n18:
        (args.out / f"n18_{rec.ident}.svg").write_text(single_n18(rec))
    for rec in n45:
        (args.out / f"n45_{rec.ident}.svg").write_text(single_n45(rec))
    (args.out / "index.html").write_text(index_html(n18, n45))


if __name__ == "__main__":
    main()
