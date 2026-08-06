#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from plane_scan.classify import canonical_fibers
from plane_scan import cubic, quartic

HERE = Path(__file__).resolve().parent
RELEASE_ROOT = HERE.parents[1]
TARGET_FILE = RELEASE_ROOT / "examples" / "data" / "four_fibre_allowable_v2.json"
OUTPUT_FILE = RELEASE_ROOT / "examples" / "data" / "coverage_56_v1.json"


def scan_family(name: str, module: object, targets: list[tuple[str, ...]]) -> dict[str, object]:
    start = perf_counter()
    print(f"[{name}] structural screening of {len(targets)} targets", flush=True)
    records = []
    verified = 0
    for index, target in enumerate(targets, start=1):
        candidate = module.structural_candidate(target)
        witness = module.WITNESSES.get(target)
        if witness is not None:
            result = module.verify(witness)
            observed = canonical_fibers(result["fibers"])
            if observed != target:
                raise AssertionError(f"{name} witness mismatch: {target} != {observed}")
            if result["euler_total"] != 12:
                raise AssertionError(f"{name} Euler total failed for {target}")
            status = "exists_verified"
            verified += 1
        elif candidate:
            result = None
            status = "candidate_without_witness"
        else:
            result = None
            status = "excluded_by_infinity_fiber"
        records.append({
            "target": list(target),
            "status": status,
            "structural_candidate": candidate,
            "witness": result,
        })
        if index % 10 == 0 or index == len(targets):
            print(f"[{name}] {index}/{len(targets)} targets; {verified} exact witnesses", flush=True)
    elapsed = perf_counter() - start
    return {
        "family": name,
        "target_count": len(targets),
        "exact_witness_count": verified,
        "candidate_without_witness_count": sum(r["status"] == "candidate_without_witness" for r in records),
        "excluded_count": sum(r["status"] == "excluded_by_infinity_fiber" for r in records),
        "wall_seconds": elapsed,
        "records": records,
    }


def main() -> None:
    source = json.loads(TARGET_FILE.read_text())
    targets = [
        canonical_fibers(item["fibers"])
        for item in source["configurations"]
        if item["j_degree"] > 0
    ]
    if len(targets) != 56:
        raise AssertionError(f"expected 56 targets, got {len(targets)}")

    cubic_result = scan_family("harmonic_plus_cubic", cubic, targets)
    quartic_result = scan_family("two_node_structured_quartic", quartic, targets)
    cubic_hits = {tuple(r["target"]) for r in cubic_result["records"] if r["status"] == "exists_verified"}
    quartic_hits = {tuple(r["target"]) for r in quartic_result["records"] if r["status"] == "exists_verified"}
    union = cubic_hits | quartic_hits
    result = {
        "scope": "56 allowable four-fiber configurations with nonconstant J",
        "families": [cubic_result, quartic_result],
        "summary": {
            "cubic_exact": len(cubic_hits),
            "quartic_exact": len(quartic_hits),
            "overlap": len(cubic_hits & quartic_hits),
            "union_exact": len(union),
            "complement_exact_within_these_two_classes": len(targets) - len(union),
        },
        "union_targets": [list(t) for t in sorted(union)],
        "complement_targets": [list(t) for t in targets if t not in union],
    }
    OUTPUT_FILE.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
