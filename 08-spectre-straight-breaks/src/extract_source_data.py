#!/usr/bin/env python3
from pathlib import Path
from spectre_straight import ROOT, write_source_data

if __name__ == "__main__":
    out = ROOT / "data"
    write_source_data(out)
    print(f"wrote source-derived data under {out}")
