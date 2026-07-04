#!/usr/bin/env python3
"""Launch Artifact 18's three exact writers and the read-only 80-column monitor."""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from v2_common import atomic_json
from v2_terminal_dashboard import Dashboard

STOP = False


def request_stop(*_: object) -> None:
    global STOP
    STOP = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=50_000)
    parser.add_argument("--workspace", type=Path, default=Path("."),
                        help="destination for generated blocks and campaign state")
    parser.add_argument("--poll", type=float, default=0.5, help="dashboard refresh seconds")
    parser.add_argument("--report-poll", type=float, default=5.0)
    parser.add_argument("--no-dashboard", action="store_true")
    parser.add_argument("--snapshot", action="store_true",
                        help="print one final 80-column monitor frame even without a TTY")
    parser.add_argument("--skip-go-test", action="store_true", help="caller already ran go test ./...")
    parser.add_argument("--no-png", action="store_true", help="write SVG telemetry only")
    args = parser.parse_args()
    if args.target < 1 or args.poll <= 0 or args.report_poll <= 0:
        raise SystemExit("positive target and polling intervals required")

    code_root = Path(__file__).resolve().parents[1]
    data_root = args.workspace.resolve()
    data_root.mkdir(parents=True, exist_ok=True)
    run_dir = data_root / "campaign" / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True)

    if not args.skip_go_test:
        subprocess.run(["go", "test", "./..."], cwd=code_root, check=True)
    (code_root / "bin").mkdir(exist_ok=True)
    subprocess.run(["go", "build", "-o", "bin/burner", "./cmd/burner"], cwd=code_root, check=True)

    children: dict[str, subprocess.Popen[str]] = {}
    logs: dict[str, object] = {}

    def start(name: str, command: list[str]) -> None:
        log = (run_dir / f"{name}.log").open("w", encoding="utf-8")
        logs[name] = log
        children[name] = subprocess.Popen(
            command, cwd=code_root, stdout=log, stderr=subprocess.STDOUT, text=True, start_new_session=True
        )

    for lane in ("d12", "24A", "24B"):
        start(lane, [
            sys.executable, str(code_root / "tools" / "run_lane_v2.py"), "--lane", lane,
            "--target", str(args.target), "--root", str(code_root), "--data-root", str(data_root),
        ])
    reporter_command = [
        sys.executable, str(code_root / "tools" / "report_v2.py"), "--root", str(data_root),
        "--poll", str(args.report_poll),
    ]
    if args.no_png:
        reporter_command.append("--no-png")
    start("reporter", reporter_command)
    atomic_json(run_dir / "processes.json", {
        "artifact": 18, "target": args.target, "workspace": str(data_root),
        "pids": {name: process.pid for name, process in children.items()},
        "utc": datetime.now(timezone.utc).isoformat(),
    })

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    dashboard = Dashboard(data_root, children, args.target)
    dashboard.start()
    exit_code = 0
    try:
        while not STOP:
            if not args.no_dashboard:
                dashboard.render(False)
            if all(children[lane].poll() is not None for lane in ("d12", "24A", "24B")):
                final_report = [sys.executable, str(code_root / "tools" / "report_v2.py"), "--root", str(data_root), "--once"]
                if args.no_png:
                    final_report.append("--no-png")
                subprocess.run(final_report, cwd=code_root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                exit_code = max((children[lane].returncode or 0) for lane in ("d12", "24A", "24B"))
                break
            time.sleep(args.poll)
    finally:
        if not args.no_dashboard:
            dashboard.render(True)
        for process in children.values():
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
        for process in children.values():
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
        if args.snapshot:
            print(dashboard.snapshot(False))
        for log in logs.values():
            log.close()
        dashboard.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
