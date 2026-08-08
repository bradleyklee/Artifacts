#!/usr/bin/env python3
"""Restartable multicore level-5 runner with staged timeout retries.

All terminal progress is hard-limited to 80 columns.  The normal level5 mode
solves the frozen unresolved queue.  Push mode reads every checkpoint, finds
classes whose best known status is still timeout, and retries only those cases.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

LINE_WIDTH = 80
DEFAULT_HEARTBEAT = 30.0
RESOLVED = {"optimal", "infeasible"}


def say(text: str) -> None:
    """Print one flushed progress line no wider than 80 columns."""
    clean = " ".join(str(text).split())
    if len(clean) > LINE_WIDTH:
        clean = clean[: LINE_WIDTH - 3] + "..."
    print(clean, flush=True)


def code_tag(code: str) -> str:
    """Return a short stable tag while keeping the full code in JSON."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:10]


def stage_tag(value: str) -> str:
    """Return a filename-safe retry-stage tag."""
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return clean.strip("._-") or "retry"


def iter_records(search: Path, pattern: str = "*.jsonl"):
    """Yield valid JSON objects from checkpoint files."""
    for path in sorted(search.glob(pattern)):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and "class_id" in record:
                yield path, record


def best_statuses(search: Path) -> dict[int, str]:
    """Combine overlapping layouts; a resolved result beats a timeout."""
    best: dict[int, str] = {}
    for _, record in iter_records(search):
        class_id = int(record["class_id"])
        status = str(record.get("status", "unknown"))
        old = best.get(class_id)
        if old in RESOLVED:
            continue
        if status in RESOLVED or old is None:
            best[class_id] = status
        elif old == "unknown" and status == "timeout":
            best[class_id] = status
    return best


def completed_for_stage(search: Path, prefix: str) -> set[int]:
    """Return all IDs already attempted in one named stage, any layout."""
    done: set[int] = set()
    for _, record in iter_records(search, f"{prefix}_shard_*_of_*.jsonl"):
        done.add(int(record["class_id"]))
    return done


def launch_workers(args: argparse.Namespace) -> int:
    """Launch workers and tee serialized progress to terminal and logs."""
    root = args.root.resolve()
    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    })
    mode = "push" if args.retry_timeouts else "level5"
    stage = args.stage or f"t{args.time_limit:g}s"
    log_stem = f"{mode}_{stage_tag(stage)}" if args.retry_timeouts else mode
    procs: list[tuple[int, subprocess.Popen[str], object]] = []
    readers: list[threading.Thread] = []
    say(
        f"[launch] mode={mode} workers={args.workers} "
        f"limit={args.time_limit:g}s"
    )

    def relay(index: int, proc: subprocess.Popen[str], log) -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            clean = line.rstrip("\r\n")
            log.write(clean + "\n")
            log.flush()
            say(f"[W{index:02d}] {clean}")
        proc.stdout.close()

    for index in range(args.workers):
        log_path = logs / f"{log_stem}_worker_{index:02d}.log"
        log = log_path.open("w", encoding="utf-8")
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--root", str(root),
            "--time-limit", str(args.time_limit),
            "--heartbeat", str(args.heartbeat),
            "--shards", str(args.workers),
            "--shard-index", str(index),
        ]
        if args.retry_timeouts:
            cmd += ["--retry-timeouts", "--stage", stage]
        if args.limit:
            cmd += ["--limit", str(args.limit)]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        procs.append((index, proc, log))
        reader = threading.Thread(
            target=relay, args=(index, proc, log), daemon=True
        )
        reader.start()
        readers.append(reader)
        say(f"[launch] worker={index:02d} pid={proc.pid} log={log_path.name}")

    failed = 0
    try:
        remaining = {index for index, _, _ in procs}
        while remaining:
            for index, proc, _ in procs:
                if index not in remaining:
                    continue
                rc = proc.poll()
                if rc is None:
                    continue
                remaining.remove(index)
                failed += rc != 0
                say(f"[launch] worker={index:02d} exit={rc}")
            if remaining:
                time.sleep(0.2)
    except KeyboardInterrupt:
        say("[launch] interrupt: terminating workers")
        for _, proc, _ in procs:
            if proc.poll() is None:
                proc.terminate()
        for _, proc, _ in procs:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        failed = -1
    finally:
        for reader in readers:
            reader.join(timeout=5)
        for _, _, log in procs:
            if not log.closed:
                log.close()
    return 130 if failed == -1 else (1 if failed else 0)


def solve_with_heartbeat(labels, solve_fixed_grid, time_limit, heartbeat, prefix):
    """Run the blocking MILP while a daemon thread reports liveness."""
    stop = threading.Event()
    started = time.monotonic()

    def beat() -> None:
        while not stop.wait(heartbeat):
            elapsed = time.monotonic() - started
            say(f"{prefix} running elapsed={elapsed:.0f}s limit={time_limit:g}s")

    thread = threading.Thread(target=beat, daemon=True)
    thread.start()
    try:
        return solve_fixed_grid(labels, 5, time_limit=time_limit)
    finally:
        stop.set()
        thread.join(timeout=max(0.1, min(heartbeat, 1.0)))


def load_manifest(root: Path) -> dict[int, dict[str, str]]:
    """Load the frozen class manifest keyed by numeric lookup ID."""
    rows: dict[int, dict[str, str]] = {}
    with (root / "results/n5_manifest.tsv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            rows[int(row["class_id"])] = row
    return rows


def run_one_shard(args: argparse.Namespace) -> int:
    import numpy as np
    from generate_reports import grid_code
    from p4_solver import solve_fixed_grid

    root = args.root
    search = root / "search"
    search.mkdir(exist_ok=True)
    manifest = load_manifest(root)

    if args.retry_timeouts:
        stage = stage_tag(args.stage or f"t{args.time_limit:g}s")
        prefix_name = f"retry_{stage}"
        current = best_statuses(search)
        candidates = {cid for cid, status in current.items() if status == "timeout"}
        stage_done = completed_for_stage(search, prefix_name)
        candidate_ids = candidates - stage_done
    else:
        prefix_name = "exact"
        unresolved_path = root / "results/n5_record6_unresolved_ids.txt"
        candidates = {int(x) for x in unresolved_path.read_text().split()}
        stage_done = completed_for_stage(search, prefix_name)
        candidate_ids = candidates - stage_done

    name = (
        f"{prefix_name}_shard_{args.shard_index:02d}_of_"
        f"{args.shards:02d}.jsonl"
    )
    out = search / name
    jobs = [
        manifest[cid]
        for cid in sorted(candidate_ids)
        if cid in manifest and cid % args.shards == args.shard_index
    ]
    if args.limit:
        jobs = jobs[: args.limit]

    mode = "push" if args.retry_timeouts else "level5"
    say(
        f"[start] mode={mode} shard={args.shard_index:02d}/"
        f"{args.shards:02d} jobs={len(jobs)}"
    )
    with out.open("a", encoding="utf-8") as handle:
        for position, row in enumerate(jobs, 1):
            class_id = int(row["class_id"])
            width = int(row["width"])
            values = (int(char) for char in row["labels_flat"])
            labels = np.fromiter(values, dtype=np.int16).reshape(width, width)
            code = grid_code(labels.tolist())
            tag = code_tag(code)
            prefix = f"[{position}/{len(jobs)}] id={class_id} tag={tag}"
            say(f"{prefix} start width={width}")
            started = time.monotonic()
            solution, status = solve_with_heartbeat(
                labels, solve_fixed_grid, args.time_limit, args.heartbeat, prefix
            )
            seconds = time.monotonic() - started
            record = {
                "class_id": class_id,
                "depth": int(row["depth"]),
                "inflation": 1,
                "code": code,
                "code_tag": tag,
                "status": status,
                "seconds": seconds,
                "stage": prefix_name,
                "time_limit": args.time_limit,
                "shard_index": args.shard_index,
                "shards": args.shards,
            }
            if solution is not None:
                record.update({
                    "taxicab_length": solution.length,
                    "normalized_value": solution.length / width,
                })
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
            handle.flush()
            length = record.get("taxicab_length", "-")
            say(f"{prefix} done status={status} L={length} sec={seconds:.2f}")
    say(f"[done] shard={args.shard_index:02d} completed={len(jobs)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--time-limit", type=float, default=120)
    parser.add_argument("--heartbeat", type=float, default=DEFAULT_HEARTBEAT)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--retry-timeouts",
        action="store_true",
        help="retry only classes whose best checkpoint status is timeout",
    )
    parser.add_argument(
        "--stage",
        default="",
        help="retry stage name; defaults to the per-case time limit",
    )
    args = parser.parse_args()

    if args.workers < 0 or args.shards < 1:
        parser.error("workers must be nonnegative; shards must be positive")
    if args.heartbeat <= 0 or args.time_limit <= 0:
        parser.error("time limit and heartbeat must be positive")
    if args.workers:
        if args.shards != 1 or args.shard_index != 0:
            parser.error("use --workers or manual shard arguments, not both")
        return launch_workers(args)
    if not 0 <= args.shard_index < args.shards:
        parser.error("--shard-index must satisfy 0 <= index < shards")
    return run_one_shard(args)


if __name__ == "__main__":
    raise SystemExit(main())
