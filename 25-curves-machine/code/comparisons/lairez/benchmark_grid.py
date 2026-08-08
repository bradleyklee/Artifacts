#!/usr/bin/env python3
"""Sequential, timeout-aware benchmark harness for the generated case grid."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str], timeout: float) -> dict:
    start = time.perf_counter()
    try:
        proc = subprocess.run(command, text=True, capture_output=True,
                              timeout=timeout, check=False)
        status = "PASS" if proc.returncode == 0 else "FAIL"
        return {"status": status, "returncode": proc.returncode,
                "wall_seconds": time.perf_counter()-start,
                "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as exc:
        return {"status": "TIMEOUT", "wall_seconds": time.perf_counter()-start,
                "stdout": exc.stdout or "", "stderr": exc.stderr or ""}


def parse_la_arg(text: str) -> dict:
    def one(label: str):
        m = re.search(rf"^{label} (.+)$", text, re.MULTILINE)
        return m.group(1) if m else None
    return {
        "setup_seconds": float(one("SETUP_SECONDS")) if one("SETUP_SECONDS") else None,
        "reduction_seconds": float(one("REDUCTION_SECONDS")) if one("REDUCTION_SECONDS") else None,
        "order": int(one("FOUND_ORDER")) if one("FOUND_ORDER") else None,
        "profile_stats": json.loads(one("PROFILE_STATS")) if one("PROFILE_STATS") else None,
        "operator": [m.group(2) for m in re.finditer(r"^P([0-9]+) (.+)$", text, re.MULTILINE)],
    }


def parse_klee(text: str) -> dict:
    start = text.find("{")
    return json.loads(text[start:]) if start >= 0 else {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pair_root", type=Path)
    ap.add_argument("--group", choices=("mixed_quartic", "pure_quartic", "pure_sextic"))
    ap.add_argument("--match", default="*")
    ap.add_argument("--lairez-timeout", type=float, default=180)
    ap.add_argument("--klee-timeout", type=float, default=300)
    ap.add_argument("--output", type=Path, default=ROOT/"grid_benchmark_latest.json")
    ap.add_argument("--engine", choices=("both", "lairez", "klee"), default="both")
    ap.add_argument("--resume", action="store_true")
    ns = ap.parse_args()
    cases = sorted((ROOT/"cases"/"grid").glob(f"{ns.match}.json"))
    py = sys.executable
    results = []
    if ns.resume and ns.output.exists():
        results = json.loads(ns.output.read_text()).get("results", [])
    completed = {row["case"] for row in results}
    for path in cases:
        case = json.loads(path.read_text())
        if ns.group and case["benchmark_group"] != ns.group:
            continue
        if case["name"] in completed:
            continue
        max_order = int(case["klee_config"]["order"])
        la = {"status": "SKIPPED", "parsed": {}}
        if ns.engine in ("both", "lairez"):
            la = run([py, str(ROOT/"lairez_port.py"), str(path),
                      "--max-order", str(max_order)], ns.lairez_timeout)
            la["parsed"] = parse_la_arg(la["stdout"])
        kl = {"status": "SKIPPED", "parsed": {}}
        if ns.engine in ("both", "klee"):
            kl = run([py, str(ROOT/"klee_triangle_square_derivation.py"),
                      str(ns.pair_root), "--case-json", str(path)], ns.klee_timeout)
            kl["parsed"] = parse_klee(kl["stdout"]) if kl["status"] == "PASS" else {}
        op_equal = (la["parsed"].get("operator") == kl["parsed"].get("operator")
                    if la["status"] == kl["status"] == "PASS" else None)
        results.append({"case": case["name"], "group": case["benchmark_group"],
                        "harmonic_terms": case["harmonic_terms"],
                        "lairez": la, "klee": kl, "operators_equal": op_equal})
        ns.output.write_text(json.dumps({"schema":"harmonic-grid-v1",
                                         "results":results}, indent=2)+"\n")
        print(case["name"], la["status"], kl["status"], op_equal, flush=True)


if __name__ == "__main__":
    main()
