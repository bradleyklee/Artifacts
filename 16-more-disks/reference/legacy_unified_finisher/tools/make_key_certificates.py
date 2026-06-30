#!/usr/bin/env python3
"""Emit standalone exact certificates for the current key witnesses."""
from __future__ import annotations
import json
from pathlib import Path
from lattice_collision.core import Body, cardinal_velocities, lattice_sites, make_container, model_for, run

OUT = Path(__file__).resolve().parents[1] / "certificates"

RECORDS = [
    # model, L, site ids, ordered cardinal velocities, cap, title
    ("square", 2, (0, 1), ("E", "N"), 20, "square_L2_N2_first_pair_corner"),
    ("octagon", 2, (0, 3), ("E", "N"), 20, "octagon_L2_N2_first_wall_corner"),
    ("octagon", 2, (0, 1, 2), ("W", "N", "S"), 256, "octagon_L2_N3_first_regular_survivor_256"),
    ("24gon", 2, (0, 1), ("E", "S"), 100, "24gon_L2_N2_first_offcardinal_survivor_100"),
]


def emit(shape: str, L: int, site_ids: tuple[int, ...], names: tuple[str, ...], cap: int, stem: str) -> dict:
    model = model_for(shape)
    sites = lattice_sites(model, L)
    velocities = cardinal_velocities(model.field)
    start = [Body(sites[site], velocities[name]) for site, name in zip(site_ids, names)]
    outcome = run(model, make_container(model, L), start, cap)
    doc = {
        "schema": "lattice-geometry-certificate/v1",
        "ordering": "model -> N -> orientation/phase -> unordered site tuple -> ordered velocity tuple",
        "model": model.wire(),
        "container": make_container(model, L).wire(),
        "case": {"L": L, "N": len(site_ids), "sites": list(site_ids), "velocities": list(names), "event_cap": cap},
        "outcome": outcome,
    }
    path = OUT / f"{stem}.json"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return {"certificate": path.name, "status": outcome["status"], "event_batches": outcome["event_batches"],
            "pair_face_contacts": len(outcome["pair_face_word"]), "max_metrics": outcome["max_metrics"]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    facts = [emit(*record) for record in RECORDS]
    (OUT / "INDEX.json").write_text(json.dumps({"schema": "lattice-geometry-certificate-index/v1", "records": facts}, indent=2) + "\n")
    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
