#!/usr/bin/env python3
"""Code-only SVG/MP4 depictions for the key exact certificates."""
from __future__ import annotations
import json
import math
import subprocess
from pathlib import Path
from fractions import Fraction
from typing import Iterable
from PIL import Image, ImageDraw, ImageFont

from lattice_collision.core import Body, Vec, cardinal_velocities, lattice_sites, make_container, model_for

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "renders"


def polygon_points(model, pos: Vec, scale: float, ox: float, oy: float) -> list[tuple[float, float]]:
    a = model.apothem.approx()
    radius = a / math.cos(math.pi / model.sides)
    cx, cy = pos.x.approx(), pos.y.approx()
    # Facet normals lie at 2pi*k/n. Vertices are halfway between normal angles.
    pts = []
    for k in range(model.sides):
        angle = 2 * math.pi * (k + 0.5) / model.sides
        x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        pts.append((ox + scale * x, oy - scale * y))
    return pts


def svg_scene(model, L: int, bodies: list[Body], title: str, subtitle: str, out: Path) -> None:
    side = 800
    pad = 75
    box = make_container(model, L).half_side.approx()
    scale = (side - 2 * pad) / (2 * box)
    ox = oy = side / 2
    colors = ("#9ac7e8", "#f0b36b", "#a8d5ba")
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{side}" height="{side}" viewBox="0 0 {side} {side}">',
             '<rect width="800" height="800" fill="#fffdf8"/>',
             f'<rect x="{ox-scale*box:.3f}" y="{oy-scale*box:.3f}" width="{2*scale*box:.3f}" height="{2*scale*box:.3f}" fill="none" stroke="#151515" stroke-width="3"/>',
             f'<text x="32" y="36" font-family="Helvetica,Arial,sans-serif" font-size="24" font-weight="700">{title}</text>',
             f'<text x="32" y="62" font-family="Helvetica,Arial,sans-serif" font-size="15">{subtitle}</text>',
             '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#222"/></marker></defs>']
    for i, body in enumerate(bodies):
        pts = polygon_points(model, body.pos, scale, ox, oy)
        pointstr = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        lines.append(f'<polygon points="{pointstr}" fill="{colors[i % len(colors)]}" fill-opacity="0.72" stroke="#202020" stroke-width="2"/>')
        cx, cy = ox + scale * body.pos.x.approx(), oy - scale * body.pos.y.approx()
        vx, vy = body.vel.x.approx(), body.vel.y.approx()
        lines.append(f'<line x1="{cx:.3f}" y1="{cy:.3f}" x2="{cx+50*vx:.3f}" y2="{cy-50*vy:.3f}" stroke="#222" stroke-width="3" marker-end="url(#arrow)"/>')
        lines.append(f'<text x="{cx+7:.3f}" y="{cy-9:.3f}" font-family="Helvetica,Arial,sans-serif" font-size="16">{chr(65+i)}</text>')
    lines.append(f'<text x="32" y="778" font-family="monospace" font-size="13">regular {model.sides}-gon • L={L} • exact {model.field.name} core; float only in this renderer</text>')
    lines.append('</svg>')
    out.write_text("\n".join(lines) + "\n")


def parse_scalar(model, d: dict):
    names = ("a",) if model.field.dimension == 1 else ("a", "b") if model.field.dimension == 2 else ("a", "b", "c", "d")
    return model.field.q(0) + model.field.zero().__class__(model.field, tuple(Fraction(d[n]) for n in names))


def parse_bodies(model, wires: list[dict]) -> list[Body]:
    ans = []
    for body in wires:
        p = body["position"]; v = body["velocity"]
        ans.append(Body(Vec(parse_scalar(model, p["x"]), parse_scalar(model, p["y"])),
                        Vec(parse_scalar(model, v["x"]), parse_scalar(model, v["y"]))))
    return ans


def lattice_certificate(stem: str) -> tuple[object, int, list[Body], dict]:
    doc = json.loads((ROOT / "certificates" / f"{stem}.json").read_text())
    case = doc["case"]
    model = model_for(doc["model"]["model_id"])
    sites = lattice_sites(model, case["L"])
    vels = cardinal_velocities(model.field)
    bodies = [Body(sites[i], vels[n]) for i, n in zip(case["sites"], case["velocities"])]
    return model, case["L"], bodies, doc


def draw_frame(model, L: int, bodies: list[Body], event_no: int, total: dict, out_png: Path) -> None:
    size, pad = 720, 68
    box = make_container(model, L).half_side.approx(); scale = (size - 2 * pad) / (2 * box); ox = oy = size / 2
    im = Image.new("RGB", (size, size), "#fffdf8")
    d = ImageDraw.Draw(im)
    d.rectangle((ox-scale*box, oy-scale*box, ox+scale*box, oy+scale*box), outline="#151515", width=3)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 22); small = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError: font = small = ImageFont.load_default()
    d.text((24, 20), f"Centered dodecagon E/N — exact event batch {event_no}", fill="#111", font=font)
    d.text((24, 48), f"T = {total['a']} + ({total['b']})√3", fill="#333", font=small)
    colors = ("#68a8d4", "#efae64")
    for i, b in enumerate(bodies):
        d.polygon(polygon_points(model, b.pos, scale, ox, oy), fill=colors[i], outline="#202020", width=2)
        cx, cy = ox+scale*b.pos.x.approx(), oy-scale*b.pos.y.approx()
        vx,vy=b.vel.x.approx(),b.vel.y.approx(); d.line((cx,cy,cx+40*vx,cy-40*vy),fill="#202020",width=3)
        d.ellipse((cx-3,cy-3,cx+3,cy+3),fill="#202020")
    im.save(out_png)


def make_event_index_mp4() -> None:
    doc = json.loads((ROOT / "certificates" / "centered_dodecagon_f1_EN_500.json").read_text())
    model = model_for("dodecagon")
    frames = ROOT / "renders" / "frames_centered_dodecagon_100"
    frames.mkdir(parents=True, exist_ok=True)
    records = doc["outcome"]["events"][:101]
    for i, rec in enumerate(records):
        bodies = parse_bodies(model, rec["post_state"])
        draw_frame(model, 2, bodies, rec["step"], rec["exact_T"], frames / f"frame_{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", str(frames / "frame_%04d.png"),
                    "-pix_fmt", "yuv420p", str(ROOT / "renders" / "centered_dodecagon_f1_EN_first100_event_batches.mp4")], check=True)


def centered_initial() -> tuple[object, int, list[Body]]:
    model = model_for("dodecagon")
    face = 1
    n = model.normals[face]
    vels = cardinal_velocities(model.field)
    # Incoming configuration, before the prescribed time-zero face collision.
    return model, 2, [Body(n.scale(-model.apothem), vels["E"]), Body(n.scale(model.apothem), vels["N"])]


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    m, L, b = centered_initial()
    svg_scene(m, L, b, "Centered dodecagon: face 1, incoming E/N", "Prescribed ordinary face contact at t=0; the 500-event certificate begins after elastic resolution.", RENDERS / "centered_dodecagon_f1_EN_initial.svg")
    for stem, title, subtitle in (
        ("square_L2_N2_first_pair_corner", "Square: first L=2 pair-corner terminal", "Sites [0,1], velocities E,N; classified at the first event."),
        ("octagon_L2_N2_first_wall_corner", "Octagon: first strict L=2 wall corner", "Sites [0,3], velocities E,N; old simultaneous buckets must not hide this contact."),
        ("octagon_L2_N3_first_regular_survivor_256", "Octagon: earliest L=2 three-body survivor", "Sites [0,1,2], velocities W,N,S; regular through 256 batches, not declared chaotic."),
        ("24gon_L2_N2_first_offcardinal_survivor_100", "24-gon: first off-cardinal survivor", "Sites [0,1], velocities E,S; regular through 100 batches and reaches tilted pair facets."),
    ):
        model, L, bodies, _ = lattice_certificate(stem)
        svg_scene(model, L, bodies, title, subtitle, RENDERS / f"{stem}_initial.svg")
    make_event_index_mp4()


if __name__ == "__main__":
    main()
