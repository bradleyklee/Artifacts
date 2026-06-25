#!/usr/bin/env python3
"""Read-only body--body pair extractor for one self-contained C4 clock certificate."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    c = json.loads(a.certificate.read_text())
    if c.get("schema") != "c4-clock-self-contained-certificate/v1":
        raise SystemExit("unsupported certificate schema")
    rows = []
    for row in c["evolution"]["ledger"]:
        events = row["events"]
        pairs = [x for x in events if x.startswith("pair:")]
        walls = [x for x in events if x.startswith("wall:")]
        for event in pairs:
            _, left, right, face = event.split(":")
            rows.append({
                "batch_index": row["index"], "time_a": row["time"]["a"],
                "time_b": row["time"]["b"], "pair_a": left, "pair_b": right,
                "face_a": face, "mixed_with_wall": str(bool(walls)).lower(),
                "batch_events": "|".join(events),
            })
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["batch_index","time_a","time_b","pair_a","pair_b","face_a","mixed_with_wall","batch_events"])
        w.writeheader(); w.writerows(rows)
    print(f"{a.out} pair_contacts={len(rows)}")

if __name__ == "__main__":
    main()
