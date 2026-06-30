from __future__ import annotations
import argparse
import json
from itertools import product
from pathlib import Path

from .core import (CARDINAL_NAMES, centered_pair_start, enumerate_lattice_starts, make_container,
                   model_for, run)


def _dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _label_earliest(model, results: list[dict]) -> dict:
    labels: dict[str, dict] = {}
    status_label = {
        "RETURN": "EARLIEST_RETURN", "PAIR_CORNER": "EARLIEST_PAIR_CORNER",
        "WALL_CORNER": "EARLIEST_WALL_CORNER", "COUPLED_SIMULTANEOUS": "EARLIEST_COUPLED_SIMULTANEOUS",
        "INDEPENDENT_WALL_BATCH": "EARLIEST_INDEPENDENT_WALL_BATCH", "CAP": "EARLIEST_REGULAR_HORIZON_SURVIVOR",
    }
    for r in results:
        outcome = r["outcome"]
        label = status_label.get(outcome["status"])
        if label and label not in labels:
            labels[label] = r["case_id"]
        if "EARLIEST_OFFCARDINAL_PAIR_FACE" not in labels:
            if any(face not in model.cardinal_faces for face in outcome["pair_face_word"]):
                labels["EARLIEST_OFFCARDINAL_PAIR_FACE"] = r["case_id"]
        if outcome["first_denominator_promotion"] is not None and "EARLIEST_DENOMINATOR_PROMOTION" not in labels:
            labels["EARLIEST_DENOMINATOR_PROMOTION"] = r["case_id"]
        if outcome["first_numerator_height_growth"] is not None and "EARLIEST_COEFFICIENT_HEIGHT_GROWTH" not in labels:
            labels["EARLIEST_COEFFICIENT_HEIGHT_GROWTH"] = r["case_id"]
    return labels


def atlas(args: argparse.Namespace) -> None:
    model = model_for(args.model)
    container = make_container(model, args.L)
    entries: list[dict] = []
    counts: dict[str, int] = {}
    for ordinal, (site_ids, velocity_names, start) in enumerate(enumerate_lattice_starts(model, args.L, args.N), 1):
        outcome = run(model, container, start, args.cap)
        case_id = f"{model.model_id}-L{args.L}-N{args.N}-{ordinal:06d}"
        entry = {"case_id": case_id, "raw_start_id": ordinal,
                 "canonical_start_id": case_id, "start": {"sites": list(site_ids), "velocities": list(velocity_names)},
                 "outcome": outcome}
        entries.append(entry)
        counts[outcome["status"]] = counts.get(outcome["status"], 0) + 1
    legacy_counts: dict[str, int] = {}
    for status, count in counts.items():
        legacy_status = "SIMULTANEOUS" if status in ("WALL_CORNER", "COUPLED_SIMULTANEOUS") else ("CORNER" if status == "PAIR_CORNER" and model.sides == 4 else status)
        legacy_counts[legacy_status] = legacy_counts.get(legacy_status, 0) + count
    doc = {"schema": "lattice-geometry-atlas/v1", "ordering": "model -> N -> orientation/phase -> canonical unordered site pair -> ordered velocity pair", "model": model.wire(),
           "container": container.wire(), "bodies": args.N, "event_cap": args.cap, "raw_starts": len(entries),
           "counts": counts, "legacy_collapsed_counts": legacy_counts, "earliest": _label_earliest(model, entries), "results": entries}
    _dump(Path(args.output), doc)
    print(json.dumps({"output": str(args.output), "raw_starts": len(entries), "counts": counts, "legacy_collapsed_counts": legacy_counts, "earliest": doc["earliest"]}, indent=2))


def centered(args: argparse.Namespace) -> None:
    model = model_for(args.model)
    container = make_container(model, args.L)
    start_info = centered_pair_start(model, args.L, args.face, args.va, args.vb)
    if start_info is None:
        raise SystemExit("incoming cardinal pair does not approach the prescribed face")
    start, initial_record = start_info
    outcome = run(model, container, start, args.cap, initial_records=[initial_record])
    doc = {"schema": "lattice-geometry-centered-certificate/v1", "ordering": "face class -> face label -> ordered incoming velocity pair -> event time/index", "model": model.wire(),
           "container": container.wire(), "case": {"face": args.face, "incoming": [args.va, args.vb], "L": args.L},
           "event_cap": args.cap, "outcome": outcome}
    _dump(Path(args.output), doc)
    print(json.dumps({"output": str(args.output), "status": outcome["status"], "event_batches": outcome["event_batches"],
                      "pair_face_contacts": len(outcome["pair_face_word"]), "max_metrics": outcome["max_metrics"]}, indent=2))


def centered_sweep(args: argparse.Namespace) -> None:
    model = model_for(args.model)
    container = make_container(model, args.L)
    entries = []
    for face in range(model.sides):
        if args.offcardinal_only and face in model.cardinal_faces:
            continue
        for va, vb in product(CARDINAL_NAMES, repeat=2):
            x = centered_pair_start(model, args.L, face, va, vb)
            if x is None:
                continue
            start, record = x
            outcome = run(model, container, start, args.cap, initial_records=[record])
            entries.append({"case_id": f"{model.model_id}-center-f{face}-{va}{vb}", "face": face, "incoming": [va, vb], "outcome": outcome})
    counts: dict[str, int] = {}
    for r in entries:
        counts[r["outcome"]["status"]] = counts.get(r["outcome"]["status"], 0) + 1
    doc = {"schema": "lattice-geometry-centered-sweep/v1", "model": model.wire(), "container": container.wire(),
           "event_cap": args.cap, "offcardinal_only": args.offcardinal_only, "raw_starts": len(entries), "counts": counts, "results": entries}
    _dump(Path(args.output), doc)
    print(json.dumps({"output": str(args.output), "raw_starts": len(entries), "counts": counts}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(prog="lattice-collision")
    sub = ap.add_subparsers(required=True)
    p = sub.add_parser("atlas")
    p.add_argument("--model", required=True, choices=["square", "octagon", "dodecagon", "24gon"])
    p.add_argument("--L", type=int, required=True)
    p.add_argument("--N", type=int, required=True)
    p.add_argument("--cap", type=int, default=100)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=atlas)
    p = sub.add_parser("centered")
    p.add_argument("--model", required=True, choices=["square", "octagon", "dodecagon", "24gon"])
    p.add_argument("--L", type=int, default=2)
    p.add_argument("--face", type=int, required=True)
    p.add_argument("--va", choices=CARDINAL_NAMES, required=True)
    p.add_argument("--vb", choices=CARDINAL_NAMES, required=True)
    p.add_argument("--cap", type=int, default=500)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=centered)
    p = sub.add_parser("centered-sweep")
    p.add_argument("--model", required=True, choices=["square", "octagon", "dodecagon", "24gon"])
    p.add_argument("--L", type=int, default=2)
    p.add_argument("--cap", type=int, default=300)
    p.add_argument("--offcardinal-only", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=centered_sweep)
    ns = ap.parse_args()
    ns.func(ns)


if __name__ == "__main__":
    main()
