#!/usr/bin/env python3
"""Independent checker for one self-contained C4 clock certificate."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("clock_core", HERE / "_check_clock_core.py")
if spec is None or spec.loader is None:
    raise SystemExit("cannot load exact C4 checker core")
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)

def embedded_seed(c: dict) -> dict:
    inst = c["instance"]
    return {
        "mask_bits": inst["mask_bits"], "mask_text": inst["mask_text"],
        "weight": len(inst["initial_state"]),
        "container": {"half_box": inst["container_half_box"]},
        "state": inst["initial_state"],
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    c = json.loads(a.certificate.read_text())
    if c.get("schema") != "c4-clock-self-contained-certificate/v1":
        raise SystemExit("unsupported certificate schema")
    report = core.check_data(embedded_seed(c), c["evolution"], "embedded")
    report["certificate"] = str(a.certificate)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"mask={report['mask_bits']:03d} rows={report['completed_batches']} ok={report['all_completed_rows_ok']} stop={report['terminal_class_independent']}")
    if not report["all_completed_rows_ok"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
