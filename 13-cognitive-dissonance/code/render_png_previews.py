#!/usr/bin/env python3
"""Optional SVG-to-PNG preview step; primary plots remain dependency-free SVG."""
from __future__ import annotations
import argparse
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--plots", type=Path, required=True)
    args = p.parse_args()
    try:
        import cairosvg
    except ImportError as exc:
        raise SystemExit("PNG previews require cairosvg; SVG plots were already generated.") from exc
    for stem in ("n18_contact_sheet", "n45_contact_sheet"):
        src = args.plots / f"{stem}.svg"
        dst = args.plots / f"{stem}.png"
        cairosvg.svg2png(url=str(src), write_to=str(dst), output_width=None, output_height=None)
        print(dst)

if __name__ == "__main__":
    main()
