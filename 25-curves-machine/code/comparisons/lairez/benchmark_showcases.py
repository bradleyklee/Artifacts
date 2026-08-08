#!/usr/bin/env python3
"""Reproducible wall-time harness for exact showcase computations.

Use only commands that produce independently checkable PASS markers. The script
records stdout, return status, timeout, wall time, and child-process peak RSS.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command, cwd, timeout):
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    tick = time.perf_counter()
    try:
        cp = subprocess.run(command, cwd=cwd, text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=timeout)
        status = "completed" if cp.returncode == 0 else "failed"
        code = cp.returncode
        output = cp.stdout
    except subprocess.TimeoutExpired as exc:
        status, code = "timeout", None
        output = (exc.stdout or "")
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
    wall = time.perf_counter() - tick
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return {"status": status, "returncode": code, "wall_seconds": wall,
            "child_maxrss_kb_process_lifetime": max(before, after),
            "output_tail": output[-4000:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--pair-root", type=Path)
    ap.add_argument("--output", type=Path,
                    default=ROOT/"benchmark_latest.json")
    ns = ap.parse_args()
    py = sys.executable
    jobs = [{
        "id": "port_triangle_square",
        "scope": "from-scratch operator derivation with witness ledger",
        "cwd": ROOT.parent,
        "command": [py, str(ROOT/"lairez_port.py"),
                    str(ROOT/"cases/triangle_square.json"), "--max-order", "3"],
    }, {
        "id": "port_square_hexagon",
        "scope": "from-scratch operator derivation attempt with witness ledger",
        "cwd": ROOT.parent,
        "command": [py, str(ROOT/"lairez_port.py"),
                    str(ROOT/"cases/square_hexagon.json"), "--max-order", "4"],
    }]
    if ns.pair_root:
        jobs.extend([{
            "id": "klee_triangle_square_trace",
            "scope": "stored-certificate reduction trace and verification",
            "cwd": ns.pair_root/"replay/triangle_square",
            "command": [py, "src/trace_triangle_square_reduction.py"],
        }, {
            "id": "klee_square_hexagon_full_derivation",
            "scope": "orders 1-4, operator, primitive and cross-comparison",
            "cwd": ns.pair_root/"replay/square_hexagon",
            "command": [py, "exact/run_reductive_nullspace.py"],
        }])
    results = []
    for job in jobs:
        runs = [run(job["command"], job["cwd"], ns.timeout)
                for _ in range(ns.repeats)]
        complete = [x["wall_seconds"] for x in runs
                    if x["status"] == "completed"]
        results.append({**{k: v for k, v in job.items()
                           if k not in ("cwd", "command")},
                        "command": job["command"], "runs": runs,
                        "median_completed_seconds":
                            statistics.median(complete) if complete else None})
    payload = {
        "schema": "period-certificate-benchmark-v1",
        "platform": platform.platform(),
        "python": sys.version,
        "python_executable": sys.executable,
        "repeats": ns.repeats,
        "timeout_seconds": ns.timeout,
        "results": results,
    }
    ns.output.write_text(json.dumps(payload, indent=2)+"\n")
    print(ns.output)


if __name__ == "__main__":
    main()

