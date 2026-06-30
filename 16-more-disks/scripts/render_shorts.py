#!/usr/bin/env python3
"""Code-rendered vertical Shorts from Go self-contained certificates.

Frames are sampled uniformly inside exact free-flight intervals.  Collision
labels, face words, and state data come only from the checked certificate JSON.
Floats are used here solely to rasterize the already-certified exact geometry.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import shutil
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "renders" / "shorts"

W, H, FPS = 720, 1280, 15
SQ2, SQ3, SQ6 = math.sqrt(2), math.sqrt(3), math.sqrt(6)

PALETTE = [(91, 157, 211), (235, 163, 77), (119, 181, 128)]
INK = (22, 24, 29)
PAPER = (250, 248, 242)
MUTED = (83, 88, 96)
GRID = (224, 221, 213)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fval(w: dict) -> float:
    return float(Fraction(w["a"])) + float(Fraction(w["b"])) * SQ2 + float(Fraction(w["c"])) * SQ3 + float(Fraction(w["d"])) * SQ6


def posvel(body: dict) -> tuple[float, float, float, float]:
    p, v = body["position"], body["velocity"]
    return fval(p["x"]), fval(p["y"]), fval(v["x"]), fval(v["y"])


def state_at(pre: list[dict], dt: float, phase: float) -> list[tuple[float, float, float, float]]:
    t = dt * phase
    out = []
    for b in pre:
        x, y, vx, vy = posvel(b)
        out.append((x + vx * t, y + vy * t, vx, vy))
    return out


def polygon_points(sides: int, apothem: float, x: float, y: float, scale: float, ox: float, oy: float) -> list[tuple[float, float]]:
    radius = apothem / math.cos(math.pi / sides)
    pts = []
    for k in range(sides):
        theta = 2 * math.pi * (k + 0.5) / sides
        pts.append((ox + scale * (x + radius * math.cos(theta)), oy - scale * (y + radius * math.sin(theta))))
    return pts


def fonts():
    candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    bold = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
    mono = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"]
    def load(paths, size):
        for path in paths:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()
    return load(bold, 30), load(candidates, 19), load(mono, 18), load(mono, 24), load(candidates, 15)

F_TITLE, F_BODY, F_MONO, F_BIGMONO, F_SMALL = fonts()


def draw_arrow(d: ImageDraw.ImageDraw, x: float, y: float, vx: float, vy: float, amount: float = 45) -> None:
    ex, ey = x + amount * vx, y - amount * vy
    d.line((x, y, ex, ey), fill=INK, width=3)
    angle = math.atan2(ey-y, ex-x)
    wing = 9
    for delta in (math.pi * 0.82, -math.pi * 0.82):
        d.line((ex, ey, ex + wing * math.cos(angle+delta), ey + wing * math.sin(angle+delta)), fill=INK, width=3)


def draw_panel(im: Image.Image, rect: tuple[int,int,int,int], model: dict, state: list[tuple[float,float,float,float]], label: str, event_label: str) -> None:
    d = ImageDraw.Draw(im)
    x0,y0,x1,y1 = rect
    d.rounded_rectangle(rect, radius=16, fill=(255,255,255), outline=(160,160,158), width=2)
    d.text((x0+18,y0+14), label, fill=INK, font=F_BODY)
    d.text((x0+18,y0+39), event_label, fill=MUTED, font=F_SMALL)
    ap = fval(model["apothem"])
    box = fval(model["cell_side"]) # L=2: half side = cell side
    inner_top, inner_bottom = y0+70, y1-20
    scale = min((x1-x0-55)/(2*box), (inner_bottom-inner_top)/(2*box))
    ox, oy = (x0+x1)/2, (inner_top+inner_bottom)/2
    d.rectangle((ox-scale*box, oy-scale*box, ox+scale*box, oy+scale*box), outline=INK, width=2)
    d.line((ox, oy-scale*box, ox, oy+scale*box), fill=GRID, width=1)
    d.line((ox-scale*box, oy, ox+scale*box, oy), fill=GRID, width=1)
    for i,(px,py,vx,vy) in enumerate(state):
        pts = polygon_points(model["sides"],ap,px,py,scale,ox,oy)
        d.polygon(pts, fill=PALETTE[i%len(PALETTE)], outline=INK)
        cx,cy=ox+scale*px,oy-scale*py
        d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=INK)
        draw_arrow(d,cx,cy,vx,vy,42)
        d.text((cx+8,cy-15),chr(65+i),fill=INK,font=F_BODY)


def render_dodecagon(cert: dict, frame_dir: Path) -> tuple[int, dict]:
    frame_dir.mkdir(parents=True, exist_ok=True)
    model=cert["model"]
    events=[r for r in cert["evolution"]["events"] if r["step"] >= 1][:120]
    pre0=cert["instance"]["pre_time_zero_state"]
    post0=cert["instance"]["post_time_zero_state"]
    trits=[cert["instance"]["face"] % 3]
    frames=[]
    # title/pre-collision lead-in: 2 seconds
    for _ in range(30):
        frames.append(("intro", pre0, 0.0, 0, 0, list(trits), "t = 0⁻  prescribed central face-1 contact"))
    # collision resolution hold: 1 sec
    for _ in range(15):
        frames.append(("intro", post0, 0.0, 0, 0, list(trits), "t = 0⁺  face-1 collision resolved"))
    current_trits=list(trits)
    for e in events:
        dt=fval(e["exact_dt"])
        for q in range(5):
            frames.append(("flight", e["pre_state"], dt, q/5, e["step"], list(current_trits), e))
        for b in e["batch"]:
            if b["kind"] == "PAIR_FACE":
                current_trits.append(b["face"] % 3)
    # endpoint
    if events:
        for _ in range(30):
            frames.append(("end", events[-1]["post_state"], 0, 0, events[-1]["step"], list(current_trits), "checked Go certificate continues beyond this cut"))
    for idx, item in enumerate(frames):
        im=Image.new("RGB",(W,H),PAPER); d=ImageDraw.Draw(im)
        d.rectangle((0,0,W,88),fill=(244,241,232))
        d.text((28,18),"DODECAGON • SPECIAL SEED",font=F_TITLE,fill=INK)
        d.text((28,55),"exact Go replay · event-indexed animation · finite prefix",font=F_SMALL,fill=MUTED)
        kind,state,dt,phase,step,word,meta = item
        # top animation panel
        draw_panel(im,(22,112,W-22,862),model,state_at(state,dt,phase),"face 1 · incoming E,N · lex-min ternary representative",f"event batch {step:03d}")
        # ternary subbar
        d.rounded_rectangle((22,886,W-22,1170),radius=16,fill=(255,255,255),outline=(160,160,158),width=2)
        d.text((42,910),"TERNARY FACE CLASSES  (pair face mod 3; t=0 contact included)",font=F_SMALL,fill=MUTED)
        display=''.join(map(str,word))
        # split into manageable grouped rows, newest symbol in ochre.
        if len(display)>90: display=display[-90:]
        groups=' '.join(display[i:i+3] for i in range(0,len(display),3))
        d.text((42,947),groups,font=F_BIGMONO,fill=INK)
        if display:
            bbox=d.textbbox((42,947),groups,font=F_BIGMONO)
            d.text((42,1002),f"pair contacts shown: {len(word):03d}   newest trit: {display[-1]}",font=F_MONO,fill=(155,86,23))
        # bottom ledger cue
        if isinstance(meta,dict):
            codes=[]
            for b in meta["batch"]:
                codes.append((f"P:{b['face']}" if b["kind"]=="PAIR_FACE" else f"W:{b['wall']}"))
            cue="batch = " + "+".join(codes)
        else:
            cue=str(meta)
        d.text((28,1200),cue,font=F_MONO,fill=MUTED)
        im.save(frame_dir / f"frame_{idx:05d}.png")
    return len(frames), {"event_batches": len(events), "pair_trits_at_cut": len(current_trits), "fps": FPS}


def render_24gon(cert_a: dict, cert_b: dict, frame_dir: Path) -> tuple[int, dict]:
    frame_dir.mkdir(parents=True, exist_ok=True)
    model=cert_a["model"]
    ea=[r for r in cert_a["evolution"]["events"] if r["step"]>=1][:75]
    eb=[r for r in cert_b["evolution"]["events"] if r["step"]>=1][:75]
    frames=[]
    for _ in range(30): frames.append((None,None,0,0))
    for a,b in zip(ea,eb):
        for q in range(8): frames.append((a,b,fval(a["exact_dt"]),q/8))
    for _ in range(30): frames.append((ea[-1],eb[-1],0,1))
    for idx,(a,b,dt,phase) in enumerate(frames):
        im=Image.new("RGB",(W,H),PAPER);d=ImageDraw.Draw(im)
        d.rectangle((0,0,W,88),fill=(244,241,232))
        d.text((28,18),"24-GON • TWO MINIMAL N=2 CLASSES",font=F_TITLE,fill=INK)
        d.text((28,55),"stacked exact replays · same batch index, separate physical clocks",font=F_SMALL,fill=MUTED)
        if a is None:
            sa=[posvel(x) for x in cert_a["instance"]["initial_state"]]
            sb=[posvel(x) for x in cert_b["instance"]["initial_state"]]
            e1=e2="initial lattice-centroid data"
            step=0
        else:
            sa=state_at(a["pre_state"],dt,phase);sb=state_at(b["pre_state"],fval(b["exact_dt"]),phase)
            def lab(e):
                tags=[f"P:{x['face']}" if x["kind"]=="PAIR_FACE" else f"W:{x['wall']}" for x in e["batch"]]
                return "+".join(tags)
            e1,e2=lab(a),lab(b);step=a["step"]
        draw_panel(im,(22,112,W-22,604),model,sa,"A  sites [0,1] · velocities (E,S)",f"batch {step:03d} · {e1}")
        draw_panel(im,(22,632,W-22,1124),model,sb,"B  sites [0,1] · velocities (W,N)",f"batch {step:03d} · {e2}")
        d.rounded_rectangle((22,1148,W-22,1252),radius=16,fill=(255,255,255),outline=(160,160,158),width=2)
        d.text((40,1170),"The two D4 classes are literal time reversals at the same sites.",font=F_BODY,fill=INK)
        d.text((40,1202),"Both are finite-horizon survivors through 100 checked batches.",font=F_SMALL,fill=MUTED)
        im.save(frame_dir / f"frame_{idx:05d}.png")
    return len(frames), {"event_batches":len(ea),"fps":FPS}


def make_mp4(frame_dir: Path, output: Path) -> None:
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",str(frame_dir/"frame_%05d.png"),"-pix_fmt","yuv420p","-movflags","+faststart",str(output)],check=True)


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    dodeca_path=ROOT/"data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap500.json"
    a_path=ROOT/"data/24gon_L2_N2/certificates/24gon_L2_N2_class_A_ES_cap100.json"
    b_path=ROOT/"data/24gon_L2_N2/certificates/24gon_L2_N2_class_B_WN_cap100.json"
    d=json.loads(dodeca_path.read_text());a=json.loads(a_path.read_text());b=json.loads(b_path.read_text())
    fd=OUT/"frames_dodecagon_lexmin";f24=OUT/"frames_24gon_two_classes"
    n_d,meta_d=render_dodecagon(d,fd);n_24,meta_24=render_24gon(a,b,f24)
    dvid=OUT/"dodecagon_special_lexmin_short.mp4";v24=OUT/"24gon_two_minimal_classes_short.mp4"
    make_mp4(fd,dvid);make_mp4(f24,v24)
    manifest={
      "schema":"artifact16-short-render-manifest/v1",
      "rendering":"Pillow/FFmpeg code render; input states from independently checked Go certificates; floating-point only for drawing.",
      "vertical_format":{"width":W,"height":H,"fps":FPS},
      "dodecagon":{"source":str(dodeca_path.relative_to(ROOT)),"sha256":sha(dodeca_path),"video":str(dvid.relative_to(ROOT)),"frames":n_d,"duration_seconds":n_d/FPS,**meta_d},
      "24gon":{"source_A":str(a_path.relative_to(ROOT)),"sha256_A":sha(a_path),"source_B":str(b_path.relative_to(ROOT)),"sha256_B":sha(b_path),"video":str(v24.relative_to(ROOT)),"frames":n_24,"duration_seconds":n_24/FPS,**meta_24},
      "combined_duration_seconds":(n_d+n_24)/FPS,
    }
    (OUT/"render_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    # MP4s plus manifest are the reproducible render deliverables; frames are
    # deterministic intermediates and need not bloat the portable artifact.
    shutil.rmtree(fd, ignore_errors=True)
    shutil.rmtree(f24, ignore_errors=True)
    print(json.dumps(manifest,indent=2))

if __name__=="__main__": main()
