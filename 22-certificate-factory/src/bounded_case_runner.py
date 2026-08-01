#!/usr/bin/env python3
"""Run one factory case with bounded time/memory and forensic checkpoints."""

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MIB = 1024 * 1024


def tree_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("q", type=int)
    parser.add_argument("--seconds", type=int, default=300)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--project-mib", type=int, default=10)
    parser.add_argument("--derive-ode-direct", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    forensic = root / "reports" / "forensics" / f"q{args.q}-{stamp}.json"
    size_before = tree_bytes(root)
    record = {
        "status": "starting",
        "q": args.q,
        "started_utc": stamp,
        "limits": {
            "wall_seconds": args.seconds,
            "address_space_mib": args.memory_mib,
            "project_mib": args.project_mib,
        },
        "project_bytes_before": size_before,
        "command": ["python3", "generate.py", str(args.q)],
        "last_completed_stage": None,
        "stderr_tail": [],
    }
    write_json(forensic, record)
    if size_before > args.project_mib * MIB:
        record.update(
            status="blocked",
            reason_code="project_size_limit",
            learned="No mathematical computation started.",
        )
        write_json(forensic, record)
        print(forensic)
        return 3

    command = [sys.executable, "generate.py", str(args.q)]
    if args.derive_ode_direct:
        command.append("--derive-ode-direct")
    record["command"] = command

    def limits() -> None:
        cap = args.memory_mib * MIB
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=args.seconds,
            preexec_fn=limits,
        )
        output = completed.stdout or ""
        stages = [line.strip() for line in output.splitlines() if "CHECK " in line or "BUILD " in line]
        record.update(
            status="completed" if completed.returncode == 0 else "failed",
            return_code=completed.returncode,
            last_completed_stage=stages[-1] if stages else None,
            output_tail=output.splitlines()[-40:],
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "")
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        stages = [line.strip() for line in output.splitlines() if "CHECK " in line or "BUILD " in line]
        record.update(
            status="blocked",
            reason_code="resource_limit",
            resource="wall_time",
            last_completed_stage=stages[-1] if stages else None,
            output_tail=output.splitlines()[-40:],
        )
    except (MemoryError, OSError) as exc:
        record.update(
            status="blocked",
            reason_code="resource_limit",
            resource="memory_or_process_start",
            exception=repr(exc),
        )

    record["elapsed_seconds"] = round(time.monotonic() - started, 6)
    record["peak_child_rss_kib"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    record["project_bytes_after"] = tree_bytes(root)
    write_json(forensic, record)
    print(forensic)
    return 0 if record["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
