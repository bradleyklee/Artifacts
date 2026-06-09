#!/usr/bin/env python3
"""Clean DH12 growth animator.

Defaults are chosen for a stable, magazine/video-friendly view:
fixed canvas, fixed tile size, fixed crop from final state, minimal sidebar.
"""
import argparse, json, importlib.util, subprocess, shutil, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SQRT3 = 3 ** 0.5

def load_mechanics(root):
    spec = importlib.util.spec_from_file_location(
        "generic_c6_bootstrap_shot",
        root / "mechanics" / "generic_c6_bootstrap_shot.py",
    )
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.BASE = root / "mechanics" / "c6_rephex_catalogues_v2"
    return g

def outmap_blank(rec):
    om = {tuple(x["key"]): x["out"] for x in rec.get("output", [])}
    blank = {tuple(x) for x in rec.get("blank_keys", [])}
    return om, blank

def replay(root, rec, target_level=5, max_steps=240):
    g = load_mechanics(root)
    T = g.target_for(rec.get("model", "dh12"), target_level)
    state = {p: T[p] for p in g.SEED}
    om, blank = outmap_blank(rec)
    node = (state, om, frozenset(blank), 0, tuple())
    frames = [dict(state)]
    trace = [{"event": "SEED", "cells": len(state), "depth": 0}]
    for _ in range(max_steps):
        st, data = g.collect_event((state, om, frozenset(blank), node[3], tuple()), T)
        if st != "BRANCH":
            trace.append({"event": st, "cells": len(state), "depth": node[3]})
            break
        sub = [k for k in data["U"].keys() if k in om]
        node2, err = g.apply_subset((state, om, frozenset(blank), node[3], tuple()), data, sub)
        if node2 is None:
            trace.append({"event": "ERROR", "error": err, "cells": len(state), "depth": node[3]})
            break
        state, _, _, depth, hist = node2
        node = (state, om, frozenset(blank), depth, hist)
        frames.append(dict(state))
        trace.append({"event": "STEP", "cells": len(state), "depth": depth})
    return frames, trace

def ax_xy(q, r):
    # pointy axial layout, stable and compact
    return (SQRT3 * (q + r / 2.0), 1.5 * r)

def hex_poly(cx, cy, s):
    pts = []
    for k in range(6):
        a = math.pi / 6 + k * math.pi / 3
        pts.append((cx + s * math.cos(a), cy + s * math.sin(a)))
    return pts

def label_color(label, palette="wire"):
    base = str(label).split(".")[0]
    if palette == "mono":
        return (238, 238, 226)
    # yellow/green wire-friendly palette
    if base.startswith("D"):
        return (236, 205, 92)
    if base.startswith("H"):
        return (118, 179, 88)
    if base in ("PASS", "CAP", "LEAF"):
        return (118, 179, 88)
    return (220, 220, 190)

def fit_transform(final_state, canvas_w, canvas_h, sidebar_w, margin, tile_size):
    plot_w = canvas_w - sidebar_w - 2 * margin
    plot_h = canvas_h - 2 * margin
    pts = [ax_xy(q, r) for (q, r) in final_state]
    minx, maxx = min(x for x, y in pts), max(x for x, y in pts)
    miny, maxy = min(y for x, y in pts), max(y for x, y in pts)
    raw_w = maxx - minx if maxx > minx else 1
    raw_h = maxy - miny if maxy > miny else 1
    # Honor explicit tile size, but shrink only if it would overflow.
    s = tile_size
    max_s = min((plot_w - 4 * tile_size) / raw_w, (plot_h - 4 * tile_size) / raw_h)
    if max_s > 0:
        s = min(tile_size, max_s)
    ox = margin + (plot_w - raw_w * s) / 2 - minx * s
    oy = margin + (plot_h - raw_h * s) / 2 - miny * s
    return s, ox, oy

def draw_frame(state, final_state, trace_item, rec, out, *,
               canvas_w=1280, canvas_h=720, sidebar_w=260, margin=28,
               tile_size=10, palette="wire", minimal=True, show_rules=False,
               target_level=5, frame_i=0, frame_n=1):
    img = Image.new("RGB", (canvas_w, canvas_h), (246, 244, 230))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    s, ox, oy = fit_transform(final_state, canvas_w, canvas_h, sidebar_w, margin, tile_size)

    # plot background
    plot_right = canvas_w - sidebar_w
    d.rectangle((0, 0, plot_right, canvas_h), fill=(248, 247, 236))
    d.rectangle((plot_right, 0, canvas_w, canvas_h), fill=(238, 236, 222))

    # cells
    for (q, r), lab in state.items():
        x, y = ax_xy(q, r)
        cx, cy = ox + x * s, oy + y * s
        d.polygon(hex_poly(cx, cy, s * 0.93), fill=label_color(lab, palette), outline=(35, 39, 30))

    # Very minimal info column
    x0 = plot_right + 18
    y = 24
    def line(txt, dy=18, fill=(38, 38, 32)):
        nonlocal y
        d.text((x0, y), txt, fill=fill, font=font)
        y += dy

    status = rec.get("status", "CLOSED_CHILL")
    cells = trace_item.get("cells", len(state))
    depth = trace_item.get("depth", 0)
    total = rec.get("cells", len(final_state))
    final_depth = rec.get("depth", depth)

    line("DH12 APEX", 20)
    line(f"{cells} / {total} cells", 18)
    line(f"depth {depth} / {final_depth}", 18)
    line(f"step {frame_i+1} / {frame_n}", 18)
    line(f"target L{target_level}", 18)
    if not minimal:
        y += 8
        line(status, 18)
        rh = str(rec.get("rule_hash", ""))[:16]
        if rh:
            line(rh, 18)
        line(f"accept {len(rec.get('output', []))}", 18)
        line(f"blank {len(rec.get('blank_keys', []))}", 18)

    if show_rules:
        y += 12
        line("rules", 18)
        # only first few, compact; no huge rule spam
        for item in rec.get("output", [])[:8]:
            k = "".join(x.replace("*", "·").replace(".", "")[-2:] for x in item.get("key", [])[-3:])
            line(f"{k} -> {item.get('out','')}", 14)

    img.save(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record")
    ap.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    ap.add_argument("--target-level", type=int, default=5)
    ap.add_argument("--outdir", default="anim_out")
    ap.add_argument("--fps", type=int, default=2)
    ap.add_argument("--mp4", action="store_true")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--sidebar-width", type=int, default=260)
    ap.add_argument("--tile-size", type=float, default=10.0)
    ap.add_argument("--margin", type=int, default=28)
    ap.add_argument("--palette", choices=["wire", "mono"], default="wire")
    ap.add_argument("--verbose-sidebar", action="store_true")
    ap.add_argument("--show-rules", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    frames_dir = outdir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    rec = json.load(open(args.record))
    frames, trace = replay(args.root.resolve(), rec, args.target_level)
    final_state = frames[-1]
    for i, st in enumerate(frames):
        ti = trace[min(i, len(trace)-1)] if trace else {"cells": len(st), "depth": i}
        draw_frame(
            st, final_state, ti, rec, frames_dir / f"frame_{i:04d}.png",
            canvas_w=args.width, canvas_h=args.height, sidebar_w=args.sidebar_width,
            margin=args.margin, tile_size=args.tile_size, palette=args.palette,
            minimal=not args.verbose_sidebar, show_rules=args.show_rules,
            target_level=args.target_level, frame_i=i, frame_n=len(frames)
        )

    (outdir / "trace.json").write_text(json.dumps(trace, indent=2))
    if args.mp4 and shutil.which("ffmpeg"):
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(args.fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-pix_fmt", "yuv420p",
            str(outdir / "growth.mp4"),
        ]
        subprocess.run(cmd, check=False)

    print(json.dumps({"frames": len(frames), "final_cells": len(frames[-1]), "outdir": str(outdir)}, indent=2))

if __name__ == "__main__":
    main()
