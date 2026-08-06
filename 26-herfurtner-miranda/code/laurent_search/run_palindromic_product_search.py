#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "palindromic_product_search.cpp"
BINARY = HERE / ".palindromic_product_search"
OUTPUT = ROOT / "examples" / "data" / "laurent_palindromic_search_d5_d6.json"

EXPECTED = {
    (4, 5): (77760, 4, 0),
    (4, 6): (3218040, 76, 0),
    (8, 5): (485760, 2, 0),
    (8, 6): (32901120, 182, 0),
    (10, 5): (339840, 42, 0),
    (10, 6): (15952920, 786, 0),
}


def main() -> None:
    subprocess.run(["g++", "-O3", "-fopenmp", "-std=c++17", str(SOURCE), "-o", str(BINARY)], check=True)
    try:
        raw = subprocess.check_output([str(BINARY)], text=True)
    finally:
        BINARY.unlink(missing_ok=True)
    payload = json.loads(raw)
    for item in payload["results"]:
        key = (item["model"], item["degree"])
        observed = (
            item["square_vectors"],
            item["third_moment_matches"],
            item["fourth_moment_matches"],
        )
        if observed != EXPECTED[key]:
            raise AssertionError((key, observed, EXPECTED[key]))
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
