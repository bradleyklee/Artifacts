#!/usr/bin/env python3
"""Artifact 18 serial exact block writer.

The code root supplies the Go producer and Python tooling.  The data root is
separate so smoke tests and reruns never mutate the delivered 50,000-event
corpus under the project root.
"""
from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from v2_common import LANES, atomic_json, contiguous_frontier, extract_end_state

STOP = False


def stop_requested(*_: object) -> None:
    global STOP
    STOP = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", required=True, choices=LANES)
    parser.add_argument("--target", type=int, default=50_000)
    parser.add_argument("--block-size", type=int, default=1_000)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Artifact 18 source root")
    parser.add_argument("--data-root", type=Path, default=None,
                        help="workspace receiving blocks/campaign state; default: --root")
    args = parser.parse_args()
    if args.target < 1 or args.block_size < 1:
        raise SystemExit("positive target and block-size required")
    if args.block_size > 65_535:
        raise SystemExit("block-size exceeds pair_steps.u16 capacity")

    code_root = args.root.resolve()
    data_root = (args.data_root or code_root).resolve()
    lane = args.lane
    config = LANES[lane]
    signal.signal(signal.SIGINT, stop_requested)
    signal.signal(signal.SIGTERM, stop_requested)

    lock = data_root / "campaign" / "locks" / f"{lane}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise SystemExit(f"lane lock exists: {lock}") from exc

    try:
        binary = code_root / "bin" / "burner"
        if not binary.exists():
            subprocess.run(["go", "build", "-o", str(binary), "./cmd/burner"], cwd=code_root, check=True)

        while not STOP:
            frontier, chain = contiguous_frontier(data_root, lane)
            status = {
                "lane": lane,
                "state": "idle",
                "accepted_collision": frontier,
                "target": args.target,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            }
            atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
            if frontier >= args.target:
                status["state"] = "target_reached"
                atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
                return 0

            count = min(args.block_size, args.target - frontier)
            start, end = frontier + 1, frontier + count
            work = data_root / "campaign" / "work" / lane / f"{start:06d}_{end:06d}"
            shutil.rmtree(work, ignore_errors=True)
            work.mkdir(parents=True)
            out = work / "run"
            command = [
                str(binary), "run", "--model", config["model"], "--seed", config["seed"],
                "--L", str(config["L"]), "--cap", str(count), "--checkpoint", str(count),
                "--require-regular", "--out-dir", str(out),
            ]
            if lane == "d12":
                command += ["--face", str(config["face"]), "--va", config["va"], "--vb", config["vb"]]
            else:
                command += ["--sites", config["sites"], "--velocities", config["velocities"]]
            if frontier:
                resume = work / "resume_start.json"
                extract_end_state(chain[-1][1], resume)
                command += ["--resume-checkpoint", str(resume), "--resume-step", str(frontier)]

            status.update({
                "state": "running", "segment_start": start, "segment_end": end,
                "started_utc": datetime.now(timezone.utc).isoformat(),
            })
            atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
            started = time.monotonic()
            run = subprocess.run(command, cwd=code_root, text=True, capture_output=True)
            elapsed = max(time.monotonic() - started, 1e-9)
            (work / "burner.stdout.log").write_text(run.stdout, encoding="utf-8")
            (work / "burner.stderr.log").write_text(run.stderr, encoding="utf-8")
            if run.returncode:
                status.update({
                    "state": "stopped_nonregular_or_error", "returncode": run.returncode,
                    "last_output": (run.stdout + run.stderr)[-4_000:],
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                })
                atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
                return run.returncode or 1

            block = data_root / "blocks" / lane / f"{lane}_{start:06d}_{end:06d}.block.tar.gz"
            block.parent.mkdir(parents=True, exist_ok=True)
            seal = [
                sys.executable, str(code_root / "tools" / "seal_block.py"), str(out),
                "--name", f"{lane}_{start:06d}_{end:06d}", "--out", str(block),
                "--repo", str(code_root), "--expect-events", str(count),
            ]
            subprocess.run(seal, cwd=code_root, check=True)
            subprocess.run([sys.executable, str(code_root / "tools" / "check_block.py"), str(block)],
                           cwd=code_root, check=True)
            # V3 compact evidence is the canonical Artifact 18 output, even on a fresh rerun.
            subprocess.run([sys.executable, str(code_root / "tools" / "compact_one.py"), str(block),
                            "--repo", str(code_root)], cwd=code_root, check=True)
            checked = subprocess.run([sys.executable, str(code_root / "tools" / "check_compact_block.py"), str(block)],
                                     cwd=code_root, text=True, capture_output=True)
            if checked.returncode:
                status.update({
                    "state": "seal_check_failed", "last_output": checked.stdout + checked.stderr,
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                })
                atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
                return 2

            status.update({
                "state": "sealed", "accepted_collision": end,
                "last_block": str(block.relative_to(data_root)),
                "events_per_second": count / elapsed,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            })
            atomic_json(data_root / "campaign" / "live" / lane / "writer_status.json", status)
            print(f"[{lane}] sealed {start:,}..{end:,}  {count / elapsed:.1f} evt/s  {block.name}", flush=True)
        return 0
    finally:
        try:
            os.close(fd)
            lock.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
