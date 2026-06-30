#!/usr/bin/env python3
"""Check unified outputs against the declared provisional transfer targets."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
expect = json.loads((ROOT / "expected/transfer_parity.json").read_text())["checks"]


def collapsed(counts: dict[str, int]) -> dict[str, int]:
    out: dict[str, int] = {}
    for status, count in counts.items():
        status = "SIMULTANEOUS" if status in ("WALL_CORNER", "COUPLED_SIMULTANEOUS") else status
        out[status] = out.get(status, 0) + count
    return out

for label, filename in (("dodecagon_L2_N2", "atlas/dodecagon_L2_N2.json"),
                        ("dodecagon_L3_N2", "atlas/dodecagon_L3_N2.json"),
                        ("24gon_L2_N2", "atlas/24gon_L2_N2.json")):
    doc = json.loads((ROOT / filename).read_text())
    actual = collapsed(doc["counts"])
    assert actual == expect[label], (label, actual, expect[label])
    print(f"{label}: OK {actual}")

out = json.loads((ROOT / "certificates/centered_dodecagon_f1_EN_500.json").read_text())["outcome"]
e = expect["centered_dodecagon_face1_EN_500"]
assert out["status"] == e["status"] and out["event_batches"] == e["event_batches"]
assert len(out["pair_face_word"]) == e["pair_faces"]
assert out["exact_T"] == e["time"]
f = out["final_metrics"]
actual = {"pos_num": f["positions"]["max_abs_numerator"], "pos_den": f["positions"]["max_denominator"],
          "vel_num": f["velocities"]["max_abs_numerator"], "vel_den": f["velocities"]["max_denominator"],
          "time_num": f["time"]["max_abs_numerator"], "time_den": f["time"]["max_denominator"]}
assert actual == e["final_metrics"], (actual, e["final_metrics"])
print("centered_dodecagon_face1_EN_500: OK")
