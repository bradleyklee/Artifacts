#!/usr/bin/env python3
"""Export canonical minimal periodic certificate records for triangle SAT search.

This reads the SAT search code from triangle_sat_search.py, finds the minimal
periodic certificates through a requested torus area, reconstructs one witness
periodic arrangement for each certificate, canonicalizes that witness by torus
translation, and writes a plain-text record file.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import importlib.util
import sys
from typing import Dict, List, Tuple


def load_triangle_module(path: Path):
    spec = importlib.util.spec_from_file_location("triangle_sat_search", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def state_name(state_edges: Tuple[int, int, int], edge_names: Tuple[str, ...]) -> str:
    return "".join(edge_names[e][0] for e in state_edges)


def canonicalize_witness(width: int, height: int, states: Tuple[int, ...]) -> Tuple[int, ...]:
    """Canonicalize by torus translation only.

    The torus search already fixes the geometry and anchor convention.  This
    function simply chooses the lexicographically least translation so records
    are stable across runs.
    """
    # state order is (j major, i, U/D).
    def shifted(dx: int, dy: int) -> Tuple[int, ...]:
        out: List[int] = []
        for j in range(height):
            for i in range(width):
                src_i = (i + dx) % width
                src_j = (j + dy) % height
                base = 2 * (src_j * width + src_i)
                out.append(states[base + 0])
                out.append(states[base + 1])
        return tuple(out)

    best = None
    for dy in range(height):
        for dx in range(width):
            cand = shifted(dx, dy)
            if best is None or cand < best:
                best = cand
    assert best is not None
    return best


def write_records(out_path: Path, records: List[dict], periodic_area: int, solver: str) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# triangle-periodic-certificates v1\n")
        f.write(f"meta periodic_area={periodic_area} solver={solver} count={len(records)}\n")
        for idx, rec in enumerate(records, start=1):
            f.write(f"record {idx}\n")
            f.write(f"mask {rec['mask_hex']}\n")
            f.write(f"bits {rec['bits']}\n")
            f.write(f"torus {rec['width']} {rec['height']}\n")
            f.write(f"rules {rec['rules']}\n")
            f.write(f"cells {len(rec['cells'])}\n")
            for cell in rec['cells']:
                labels = " ".join(cell['edges'])
                f.write(f"state {cell['orient']} {cell['i']} {cell['j']} {labels}\n")
            f.write("end\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-script", default="triangle_sat_search.py", help="path to triangle_sat_search.py")
    parser.add_argument("--periodic-depth", type=int, default=10, help="test ordered W×H tori with W*H <= this area")
    parser.add_argument("--solver", default="glucose4", help="PySAT solver backend")
    parser.add_argument("--output", required=True, help="output text record path")
    args = parser.parse_args()

    mod = load_triangle_module(Path(args.search_script))
    dims = mod.tori_through_area(args.periodic_depth)
    certs, _ = mod.periodic_certificates(dims, args.solver)
    certs = sorted(certs, key=lambda x: (x[0].bit_count(), x[0], x[1] * x[2], x[1], x[2]))

    records = []
    for cert, width, height in certs:
        encoding = mod.EncodedGeometry(mod.torus(width, height), args.solver)
        try:
            witness = encoding.solve(cert, want_witness=True)
        finally:
            encoding.close()
        if witness is None:
            raise RuntimeError(f"certificate 0x{cert:04x} did not solve on declared torus {width}x{height}")
        states = canonicalize_witness(width, height, witness.states)
        cells = []
        idx = 0
        for j in range(height):
            for i in range(width):
                for orient in ("U", "D"):
                    state_edges = mod.STATES[states[idx]]
                    idx += 1
                    cells.append({
                        "orient": orient,
                        "i": i,
                        "j": j,
                        "edges": tuple(mod.EDGE_NAMES[e] for e in state_edges),
                        "state_name": state_name(state_edges, mod.EDGE_NAMES),
                    })
        records.append({
            "mask": cert,
            "mask_hex": f"0x{cert:04x}",
            "bits": cert.bit_count(),
            "width": width,
            "height": height,
            "rules": mod.mask_rules(cert),
            "cells": cells,
        })

    out_path = Path(args.output)
    write_records(out_path, records, args.periodic_depth, args.solver)
    print(f"wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
