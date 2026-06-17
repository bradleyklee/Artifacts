#!/usr/bin/env python3
"""Validate DH12 seed/search records by replaying their accept/reject tables.

This is intentionally small and imports the replay semantics from
mini_dh12_sparse_search.py so the smoke-search and seed-validation paths use
one convention.
"""
import argparse, json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mini_dh12_sparse_search import parse_record, replay, digest  # noqa:E402


def state_dict(rec):
    return {(int(q), int(r)): str(s) for q, r, s in rec.get("state", [])}


def validate_record(rec, source, line):
    acc, rej = parse_record(rec)
    ev = replay(acc, rej)
    expected_state = state_dict(rec)
    exact_state = expected_state == ev["state"] if expected_state else None
    expected_cells = rec.get("cells", rec.get("_cells"))
    rule_hash = rec.get("rule_hash", rec.get("_hash"))
    return {
        "source": str(source),
        "line": line,
        "declared_hash": rule_hash,
        "replay_hash": digest(acc, rej),
        "hash_matches_prefix16": (rule_hash == digest(acc, rej)) if rule_hash else None,
        "declared_cells": expected_cells,
        "replay_cells": ev["cells"],
        "cells_match": (int(expected_cells) == ev["cells"]) if expected_cells is not None else None,
        "exact_state_match": exact_state,
        "terminal_step": ev["terminal_step"],
        "terminal_births": ev["terminal_births"],
        "terminal_unknown_frontier": ev["unknown"],
        "closed_zero_unknown": ev["terminal_births"] == 0 and ev["unknown"] == 0,
        "used_accept": ev["used_accept"],
        "used_reject": ev["used_reject"],
        "accept": len(acc),
        "reject": len(rej),
        "accept_reject_overlap": len(set(acc) & set(rej)),
    }


def iter_records(paths):
    for path in paths:
        p = Path(path)
        if p.suffix == ".jsonl":
            with p.open() as f:
                for i, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    yield p, i, json.loads(line)
        elif p.suffix == ".json":
            yield p, 1, json.loads(p.read_text())
        else:
            raise SystemExit(f"Unsupported record file type: {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", nargs="+", required=True)
    ap.add_argument("--out-jsonl")
    ap.add_argument("--min-total", type=int, default=1)
    ap.add_argument("--min-closed-zero-unknown", type=int, default=1)
    ap.add_argument("--min-exact", type=int, default=0)
    ap.add_argument("--min-max-cells", type=int, default=0)
    ns = ap.parse_args()

    rows = [validate_record(rec, src, line) for src, line, rec in iter_records(ns.records)]
    counts = Counter(str(r["replay_cells"]) for r in rows)
    summary = {
        "ok": True,
        "records": len(rows),
        "closed_zero_unknown": sum(1 for r in rows if r["closed_zero_unknown"]),
        "exact_state_matches": sum(1 for r in rows if r["exact_state_match"] is True),
        "cell_count_matches": sum(1 for r in rows if r["cells_match"] is True),
        "max_replay_cells": max([r["replay_cells"] for r in rows], default=0),
        "by_replay_cells": dict(sorted(counts.items(), key=lambda kv: int(kv[0]))),
        "overlap_records": sum(1 for r in rows if r["accept_reject_overlap"]),
    }
    failures = []
    if summary["records"] < ns.min_total:
        failures.append(f"records {summary['records']} < {ns.min_total}")
    if summary["closed_zero_unknown"] < ns.min_closed_zero_unknown:
        failures.append(f"closed_zero_unknown {summary['closed_zero_unknown']} < {ns.min_closed_zero_unknown}")
    if summary["exact_state_matches"] < ns.min_exact:
        failures.append(f"exact_state_matches {summary['exact_state_matches']} < {ns.min_exact}")
    if summary["max_replay_cells"] < ns.min_max_cells:
        failures.append(f"max_replay_cells {summary['max_replay_cells']} < {ns.min_max_cells}")
    if summary["overlap_records"] != 0:
        failures.append(f"overlap_records {summary['overlap_records']} != 0")
    if failures:
        summary["ok"] = False
        summary["failures"] = failures

    if ns.out_jsonl:
        Path(ns.out_jsonl).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.out_jsonl).write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
