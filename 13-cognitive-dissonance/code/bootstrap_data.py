#!/usr/bin/env python3
"""One-time data bootstrap used when this archive was assembled.

It reads the two supplied textual certificates and writes the normalized JSON
fixtures consumed by the verifier/renderer.  The production checker does not
trust any float conversions; all numbers remain rational strings.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_pair(s: str):
    a, b = [x.strip() for x in s.split(',')]
    return [a, b]


def parse_points(s: str):
    return [[int(a), int(b)] for a, b in re.findall(r'(-?\d+),(-?\d+)', s)]


def n18(src: str):
    raw = {}
    for m in re.finditer(
        r'^\s*(W[1-4])\s+\(([^)]*)\)\s+([^\s]+)\s+\(([^)]*)\)\s+([^\s]+)\s*$',
        src,
        re.M,
    ):
        # Match raw-to-physical table lines only: centroid-like field here is raw C2.
        ident, c2, raw_r2, _c_physical, _r2 = m.groups()
        raw[ident] = {"raw_C2": parse_pair(c2), "raw_r2": raw_r2}
    # The table pattern is intentionally constrained; exactly four raw entries required.
    if set(raw) != {"W1", "W2", "W3", "W4"}:
        raise ValueError(f"could not parse all N=18 raw rows: {raw}")
    cells = {}
    for m in re.finditer(r'^\s*(W[1-4]):\s+((?:-?\d+,-?\d+\s*)+)$', src, re.M):
        cells[m.group(1)] = parse_points(m.group(2))
    if set(cells) != set(raw):
        raise ValueError("could not parse all N=18 cell lists")
    return {
        "schema": "circle-lattice-mwe/n18-v1",
        "model": "closed disk containing entire unit squares",
        "coordinate_convention": "standard lower-left-corner grid; each listed (i,j) is [i,i+1] x [j,j+1]",
        "witnesses": [
            {"id": ident, **raw[ident], "cells": cells[ident]}
            for ident in sorted(raw)
        ],
    }


def n45(src: str):
    table = {}
    pat = re.compile(
        r'^\s*(S\d{2})\s+\(([^)]*)\)\s+\(([-?\d]+),\s*([-?\d]+)\)--\(([-?\d]+),\s*([-?\d]+)\)\s+([-?\d/]+)\s+\(([^)]*)\)\s+([-?\d/]+)\s*$',
        re.M,
    )
    for m in pat.finditer(src):
        ident, centroid, ax, ay, bx, by, t, center, r2 = m.groups()
        table[ident] = {
            "site_centroid": parse_pair(centroid),
            "anchor_A": [int(ax), int(ay)],
            "anchor_B": [int(bx), int(by)],
            "t": t,
            "expected_center": parse_pair(center),
            "expected_r2": r2,
        }
    if len(table) != 12:
        raise ValueError(f"could not parse 12 N=45 table rows: {sorted(table)}")
    sites = {}
    for m in re.finditer(r'^\s*(S\d{2}) sites:\s+((?:-?\d+,-?\d+\s*)+)$', src, re.M):
        sites[m.group(1)] = parse_points(m.group(2))
    if set(sites) != set(table):
        raise ValueError("could not parse all N=45 site lists")
    return {
        "schema": "circle-lattice-mwe/n45-v1",
        "model": "closed disk lattice-site set / polystick",
        "coordinate_convention": "physical integer lattice Z^2",
        "witnesses": [
            {"id": ident, **table[ident], "sites": sites[ident]}
            for ident in sorted(table)
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n18", type=Path, required=True)
    p.add_argument("--n45", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "n18_witnesses.json").write_text(json.dumps(n18(args.n18.read_text()), indent=2) + "\n")
    (args.out_dir / "n45_witnesses.json").write_text(json.dumps(n45(args.n45.read_text()), indent=2) + "\n")


if __name__ == "__main__":
    main()
