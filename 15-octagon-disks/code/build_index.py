#!/usr/bin/env python3
"""Build the small top-level data index from checked stored records."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: Path): return json.loads(path.read_text())

def main() -> None:
    data = {"schema": "octagon-collisions-index/v1", "families": {}}
    for family in ("three-body", "clock"):
        rows = []
        for cert in sorted((ROOT / "data" / family / "evolve").glob("*.json")):
            c = load(cert)
            inst, evo = c["instance"], c["evolution"]
            ident = str(inst.get("class", inst.get("id")))
            item = {
                "id": ident,
                "bodies": inst["body_count"],
                "batches": evo["completed_batches"],
                "stop_class": evo["stop_class"],
                "initial": f"data/{family}/initial/{ident}.json",
                "evolve": f"data/{family}/evolve/{ident}.json",
                "check": f"data/{family}/check/{ident}.json",
                "pairs": f"data/{family}/pairs/{ident}.csv",
                "image": f"data/{family}/images/{ident}.svg",
            }
            if family == "three-body": item["ternary"] = f"data/{family}/ternary/{ident}.csv"
            rows.append(item)
        data["families"][family] = rows
    (ROOT / "index.json").write_text(json.dumps(data, indent=2) + "\n")

if __name__ == "__main__": main()
