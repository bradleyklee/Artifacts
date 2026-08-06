#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAL = ROOT / "examples" / "data" / "laurent_palindromic_search_d5_d6.json"
RANK2 = ROOT / "examples" / "data" / "laurent_rank2_search_box.json"
EXPECTED = {
    (4, 5): (77760, 4, 0),
    (4, 6): (3218040, 76, 0),
    (8, 5): (485760, 2, 0),
    (8, 6): (32901120, 182, 0),
    (10, 5): (339840, 42, 0),
    (10, 6): (15952920, 786, 0),
}


def main() -> None:
    pal = json.loads(PAL.read_text())
    seen = {}
    for item in pal["results"]:
        key = (item["model"], item["degree"])
        seen[key] = (
            item["square_vectors"],
            item["third_moment_matches"],
            item["fourth_moment_matches"],
        )
    if seen != EXPECTED:
        raise AssertionError((seen, EXPECTED))
    rank2 = json.loads(RANK2.read_text())
    if rank2["support_box"]["distinct_support_sets_examined"] != 495:
        raise AssertionError("rank-2 support count changed")
    if rank2["status"] != "exact_bounded_exclusion":
        raise AssertionError("rank-2 status changed")
    print("recorded Laurent search results verified")


if __name__ == "__main__":
    main()
