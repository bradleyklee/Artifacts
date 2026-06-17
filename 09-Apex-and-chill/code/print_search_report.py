#!/usr/bin/env python3
"""Print an 80-column summary for the mutate/mate/adopt search."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def line(label: str, value) -> None:
    print(f"{label:<28} {value}")


def print_map(title: str, data: dict) -> None:
    print(f"{title}:")
    if not data:
        print("  {}")
        return
    for key in sorted(data, key=str):
        print(f"  {key}: {data[key]}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: print_search_report.py POLICY_SEARCH_SUMMARY_JSON",
              file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    s = json.loads(path.read_text())
    status = "PASS" if s.get("ok") else "NO HIT"

    print()
    print(f"Apex 852 same-family search: {status}")
    print("--------------------------------")
    line("Loaded seed records:", s.get("loaded_records"))
    line("Valid closed parents:", s.get("valid_parent_records"))
    line("Prior universe keys:", s.get("prior_universe_keys"))
    line("Signpost genes:", s.get("signpost_genes"))
    line("Target found count:", s.get("target_found"))
    line("Stop after target:", s.get("stop_after_max_found"))
    line("Min trials before stop:",
         s.get("min_trials_before_stop"))
    line("New chills >= keep_min:",
         s.get("new_closed_chill_ge_keep_min"))
    line("New terminal states:",
         s.get("new_distinct_terminal_states_ge_keep_min"))
    line("Best new cell count:", s.get("best_new_cells"))
    line("All operator blocks:",
         s.get("all_operator_blocks_entered"))
    print_map("Operator trials", s.get("operator_trials", {}))
    print_map("Found by cell count", s.get("found_by_cells", {}))
    print_map("Found by operator/cells", s.get("found_by_operator_cells", {}))

    best = s.get("best_closed_chill_candidate")
    if best:
        print("Best closed candidate:")
        print(f"  cells={best.get('cells')} method={best.get('operator')}")
        print(f"  hash={best.get('hash')}")
    trial = s.get("best_trial_seen_even_if_open")
    if trial:
        print("Best trial seen, even if open:")
        print(f"  cells={trial.get('cells')} method={trial.get('operator')}")
        print(f"  status={trial.get('status')}")
    print("Candidates directory:")
    print(f"  {s.get('candidate_dir')}")
    print("Detailed summary JSON:")
    print(f"  {path}")
    print()
    return 0 if s.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
