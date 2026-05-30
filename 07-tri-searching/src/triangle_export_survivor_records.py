#!/usr/bin/env python3
"""Export depth-completion witness records for surviving triangle rule masks."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import List


def load_triangle_module(path: Path):
    spec = importlib.util.spec_from_file_location("triangle_sat_search", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def periodic_filter(mod, space, periodic_depth: int, solver: str) -> List[int]:
    dims = mod.tori_through_area(periodic_depth)
    certs, _ = mod.periodic_certificates(dims, solver, space)
    periodic_masks = {mask for mask in range(space.full_mask + 1)
                      if any(mod.covers(mask, cert) for cert, _, _ in certs)}
    return [mask for mask in range(space.full_mask + 1) if mask not in periodic_masks]


def completion_survivors(mod, space, masks: List[int], completion_depth: int, solver: str) -> List[int]:
    alive = list(masks)
    for depth in range(1, completion_depth + 1):
        encoding = mod.EncodedGeometry(mod.completion_patch(depth), solver, space)
        try:
            alive = [mask for mask in alive if encoding.solve(mask) is not None]
        finally:
            encoding.close()
    return alive


def write_records(out_path: Path, records: List[dict], periodic_depth: int,
                  completion_depth: int, solver: str, family: str) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# triangle-survivor-configurations v1\n")
        f.write(
            f"meta family={family} periodic_area={periodic_depth} completion_depth={completion_depth} "
            f"solver={solver} count={len(records)}\n"
        )
        for idx, rec in enumerate(records, start=1):
            f.write(f"record {idx}\n")
            f.write(f"mask {rec['mask_hex']}\n")
            f.write(f"bits {rec['bits']}\n")
            f.write(f"depth {rec['depth']}\n")
            f.write(f"rules {rec['rules']}\n")
            f.write(f"cells {len(rec['cells'])}\n")
            for cell in rec['cells']:
                labels = " ".join(cell['edges'])
                f.write(f"state {cell['orient']} {cell['i']} {cell['j']} {labels}\n")
            f.write("end\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-script", default="triangle_sat_search.py",
                        help="path to triangle_sat_search.py")
    parser.add_argument("--periodic-depth", type=int, default=10,
                        help="test ordered W×H tori with W*H <= this area")
    parser.add_argument("--completion-depth", type=int, default=7,
                        help="require completion through this depth")
    parser.add_argument("--solver", default="glucose4", help="PySAT solver backend")
    parser.add_argument("--family", choices=("anchored", "unrestricted"), default="anchored", help="rule family; default anchored")
    parser.add_argument("--output", required=True, help="output text record path")
    args = parser.parse_args()

    mod = load_triangle_module(Path(args.search_script))
    space = mod.rule_space(args.family)
    alive = periodic_filter(mod, space, args.periodic_depth, args.solver)
    alive = completion_survivors(mod, space, alive, args.completion_depth, args.solver)
    patch = mod.completion_patch(args.completion_depth)
    encoding = mod.EncodedGeometry(patch, args.solver, space)
    records = []
    try:
        for mask in alive:
            witness = encoding.solve(mask, want_witness=True)
            if witness is None:
                raise RuntimeError(f"survivor mask 0x{mask:04x} failed at depth {args.completion_depth}")
            cells = []
            for idx, cell in enumerate(patch.cells):
                state_edges = mod.STATES[witness.states[idx]]
                cells.append({
                    "orient": cell[0],
                    "i": cell[1],
                    "j": cell[2],
                    "edges": tuple(mod.EDGE_NAMES[e] for e in state_edges),
                })
            records.append({
                "mask": mask,
                "mask_hex": f"0x{mask:0{max(4, (space.bits + 3) // 4)}x}",
                "bits": mask.bit_count(),
                "depth": args.completion_depth,
                "rules": mod.mask_rules(space, mask),
                "cells": cells,
            })
    finally:
        encoding.close()

    records.sort(key=lambda rec: (rec["bits"], rec["mask"]))
    out_path = Path(args.output)
    write_records(out_path, records, args.periodic_depth, args.completion_depth, args.solver, args.family)
    print(f"wrote {len(records)} survivor records to {out_path}")


if __name__ == "__main__":
    main()
