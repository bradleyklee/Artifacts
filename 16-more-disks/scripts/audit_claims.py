#!/usr/bin/env python3
"""Small deterministic gate for the public finite-prefix statements.

This does not recompute physics; it verifies that the public summaries agree
with already independent-checked Go outputs and derived data.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def need(got, want, label: str) -> None:
    if got != want:
        raise SystemExit(f"FAIL {label}: got {got!r}, want {want!r}")


def main() -> None:
    expected = {
        "data/square_L2_N4/atlas.json": {"COUPLED_SIMULTANEOUS": 24, "PAIR_CORNER": 168, "RETURN": 32, "WALL_CORNER": 32},
        "data/dodecagon_L2_N2/atlas.json": {"PAIR_CORNER": 24, "RETURN": 64, "WALL_CORNER": 8},
        "data/dodecagon_L3_N2/atlas.json": {"PAIR_CORNER": 136, "RETURN": 424, "WALL_CORNER": 16},
        "data/dodecagon_centered/atlas_all_faces_cap500.json": {"CAP": 16, "PAIR_CORNER": 32, "RETURN": 20},
        "data/dodecagon_centered/atlas_offcardinal_cap500.json": {"CAP": 16, "PAIR_CORNER": 16, "RETURN": 16},
        "data/24gon_L2_N2/atlas.json": {"CAP": 16, "RETURN": 72, "WALL_CORNER": 8},
        "data/octagon_L2_N3/atlas.json": {"CAP": 16, "COUPLED_SIMULTANEOUS": 16, "PAIR_CORNER": 88, "RETURN": 80, "WALL_CORNER": 56},
    }
    for path, counts in expected.items():
        doc = load(path)
        need(doc["counts"], counts, path + ".counts")
        if "CAP" not in counts:
            need(doc["counts"].get("CAP", 0), 0, path + ".CAP")

    report = load("analysis/symmetry_and_sequence_audit.json")
    d = report["dodecagon_centered"]["lexicographically_minimal"]
    need(d["case_id"], "dodecagon-center-f1-EN", "dodecagon lex-min case")
    need(d["face"], 1, "dodecagon lex-min face")
    need(d["incoming"], ["E", "N"], "dodecagon lex-min incoming")
    need(report["dodecagon_centered"]["distinct_ternary_words"], 2, "dodecagon ternary classes")
    need(len(report["24gon_L2_N2"]["D4_classes"]), 2, "24-gon D4 classes")
    for cls in report["24gon_L2_N2"]["D4_classes"]:
        if not cls["time_reverse_same_sites"]:
            raise SystemExit("FAIL 24-gon class lacks time-reverse CAP image")

    seq = report["dodecagon_sequences"]
    need(seq["full_cap2000"]["pair_contacts"], 418, "dodecagon cap2000 pair contacts")
    need(seq["compact_cap7500"]["pair_contacts"], 1578, "dodecagon cap7500 pair contacts")
    need(seq["reverse_stem"]["regular_ternary_word"], "1", "reverse stem trit")
    need(seq["reverse_stem"]["terminal_status"], "PAIR_CORNER", "reverse stem terminal")

    for path in (ROOT / "check").glob("*.python.json"):
        need(load(str(path.relative_to(ROOT)))["result"], "PASS", str(path.relative_to(ROOT)))
    print("ARTIFACT16_PUBLIC_CLAIM_AUDIT=PASS")


if __name__ == "__main__":
    main()
