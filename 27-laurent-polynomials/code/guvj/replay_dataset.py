#!/usr/bin/env python3
"""Replay a G,U,V,J dataset one model per subprocess and aggregate the report."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRATCH_ROOT = PROJECT_ROOT / ".tmp"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--timeout", type=float, default=360.0)
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root.is_absolute():
        data_root = PROJECT_ROOT / data_root
    report_path = args.report or (data_root / "REPLAY_REPORT.json")
    if not report_path.is_absolute():
        report_path = PROJECT_ROOT / report_path

    models = read_json(data_root / "models.json")["models"]
    results = []
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="guvj-replay-", dir=SCRATCH_ROOT
    ) as temporary:
        temporary_root = Path(temporary)
        for index, model in enumerate(models, start=1):
            name = model["model"]
            part = temporary_root / f"{name}.json"
            print(f"[{index}/{len(models)}] replay {name} in fresh process", flush=True)
            subprocess.run(
                [
                    sys.executable,
                    str(CODE_ROOT / "verify_reference.py"),
                    "--data-root", str(data_root),
                    "--model", name,
                    "--report", str(part),
                ],
                cwd=PROJECT_ROOT,
                check=True,
                timeout=args.timeout,
            )
            payload = read_json(part)
            if len(payload["models"]) != 1:
                raise AssertionError(f"unexpected replay report for {name}")
            results.extend(payload["models"])

    report = {
        "schema": "laurent-period-guvj-replay-report-v1",
        "data_root": str(data_root.relative_to(PROJECT_ROOT)),
        "models": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(results)}/{len(models)} G,U,V,J records", flush=True)
    print(f"report: {report_path}", flush=True)


if __name__ == "__main__":
    main()
