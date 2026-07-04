#!/usr/bin/env python3
"""Accept only a completed, single-surface exact two-body ledger.

This is deliberately a campaign gate, not a physics resolver.  Any wall/pair
same-time batch, wall corner, pair corner, missing hash, or unexpected event
class is written into the audit report and returns nonzero.
"""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger", type=Path)
    ap.add_argument("summary", type=Path)
    ap.add_argument("--expect-batches", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    failures: list[dict] = []
    kind_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    rows = 0
    first_step: int | None = None
    last_step: int | None = None

    with gzip.open(args.ledger, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            row = json.loads(line)
            rows += 1
            step = row.get("step")
            first_step = step if first_step is None else first_step
            last_step = step
            cls = row.get("event_class")
            batch = row.get("batch", [])
            class_counts[str(cls)] += 1
            if cls != "REGULAR":
                failures.append({"line": line_no, "step": step, "reason": "non_regular_class", "value": cls})
            if len(batch) != 1:
                failures.append({"line": line_no, "step": step, "reason": "non_singleton_batch", "size": len(batch)})
                continue
            event = batch[0]
            kind = event.get("kind")
            kind_counts[str(kind)] += 1
            if kind not in {"WALL_FACE", "PAIR_FACE"}:
                failures.append({"line": line_no, "step": step, "reason": "non_surface_event", "kind": kind})
            if kind == "WALL_FACE" and not event.get("wall"):
                failures.append({"line": line_no, "step": step, "reason": "wall_missing_label"})
            if kind == "PAIR_FACE" and event.get("face") is None:
                failures.append({"line": line_no, "step": step, "reason": "pair_missing_face"})
            if not row.get("pre_state_hash") or not row.get("post_state_hash"):
                failures.append({"line": line_no, "step": step, "reason": "missing_state_hash"})

    summary = load_json(args.summary)
    if summary.get("status") not in {"CAP", "RETURN"}:
        failures.append({"reason": "terminal_status", "status": summary.get("status")})
    if not summary.get("regular_only_completed", summary.get("status") in {"CAP", "RETURN"}):
        failures.append({"reason": "summary_regular_policy_failed"})
    if rows != args.expect_batches:
        failures.append({"reason": "wrong_batch_count", "expected": args.expect_batches, "actual": rows})

    report = {
        "schema": "single-surface-audit/v1",
        "accepted": not failures,
        "expected_batches": args.expect_batches,
        "observed_batches": rows,
        "first_step": first_step,
        "last_step": last_step,
        "summary_status": summary.get("status"),
        "event_classes": dict(class_counts),
        "event_kinds": dict(kind_counts),
        "failures": failures,
        "policy": "every retained batch must be exactly one WALL_FACE or one PAIR_FACE; all coupled/simultaneous/corner cases are terminal and rejected",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("accepted", "observed_batches", "summary_status", "event_classes", "event_kinds")}, sort_keys=True))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
