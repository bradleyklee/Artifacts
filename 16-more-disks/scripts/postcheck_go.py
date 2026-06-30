#!/usr/bin/env python3
"""Independent Python post-check for artifact-16 Go output.

This script deliberately imports only the legacy Python exact core, never the
Go producer.  It recreates every start from the JSON seed metadata and checks
the globally generated event path against Go's stored ledger.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lattice_collision import core as pycore
from lattice_collision.core import Body, Vec, cardinal_velocities, centered_pair_start, lattice_sites, make_container, model_for
from lattice_collision.exact import E
from itertools import combinations

GO_BASIS_INDEX = {0: "a", 1: "b", 2: "c", 3: "d"}


def fail(path: str, message: str) -> None:
    raise AssertionError(f"{path}: {message}")


def scalar_matches(go: dict, py, path: str) -> None:
    expected = {"a": Fraction(0), "b": Fraction(0), "c": Fraction(0), "d": Fraction(0)}
    for mask, value in zip(py.field.basis_masks, py.c):
        expected[GO_BASIS_INDEX[mask]] = value
    for key, want in expected.items():
        got = Fraction(go[key])
        if got != want:
            fail(path + "." + key, f"got {got}, want {want}")


def vec_matches(go: dict, py, path: str) -> None:
    scalar_matches(go["x"], py.x, path + ".x")
    scalar_matches(go["y"], py.y, path + ".y")


def body_matches(go: dict, py, path: str) -> None:
    vec_matches(go["position"], py.pos, path + ".position")
    vec_matches(go["velocity"], py.vel, path + ".velocity")


def batch_matches(go_batch: list[dict], py_batch: list[dict], path: str) -> None:
    if len(go_batch) != len(py_batch):
        fail(path, f"batch length got {len(go_batch)} want {len(py_batch)}")
    for i, (g, p) in enumerate(zip(go_batch, py_batch)):
        q = f"{path}[{i}]"
        if g["kind"] != p["kind"]:
            fail(q + ".kind", f"got {g['kind']} want {p['kind']}")
        if g["bodies"] != p["bodies"]:
            fail(q + ".bodies", f"got {g['bodies']} want {p['bodies']}")
        if g["face"] != p["face"]:
            fail(q + ".face", f"got {g['face']} want {p['face']}")
        if g["wall"] != p["wall"]:
            fail(q + ".wall", f"got {g['wall']} want {p['wall']}")
        scalar_matches(g["dt"], _scalar_from_wire(p["dt"], _field_from_scalar_wire(p["dt"])), q + ".dt")


def _field_from_scalar_wire(wire: dict):
    # This helper is unused in normal comparisons because event scalars get
    # checked directly by rational coordinates below. It remains here to keep
    # batch checking explicit about not relying on Go's floating render data.
    raise RuntimeError("internal helper should not be called")


def scalar_wire_matches(go: dict, py_wire: dict, model, path: str) -> None:
    # Convert a Python wire that omits unused basis coordinates to Go's 4-basis.
    masks = model.field.basis_masks
    global_names = {0: "a", 1: "b", 2: "c", 3: "d"}
    compact_names = {1: ("a",), 2: ("a", "b"), 4: ("a", "b", "c", "d")}[len(masks)]
    expected = {"a": Fraction(0), "b": Fraction(0), "c": Fraction(0), "d": Fraction(0)}
    for mask, compact_name in zip(masks, compact_names):
        expected[global_names[mask]] = Fraction(py_wire[compact_name])
    for key, want in expected.items():
        got = Fraction(go[key])
        if got != want:
            fail(path + "." + key, f"got {got}, want {want}")


def compare_metrics(go: dict, py: dict, path: str) -> None:
    for src, dst in (("positions", "positions"), ("velocities", "velocities"), ("all_coordinates", "all_coordinates")):
        for key in ("max_abs_numerator", "max_denominator", "max_numerator_bits", "max_denominator_bits"):
            got = str(go[src][key])
            want = str(py[dst][key])
            if got != want:
                fail(f"{path}.{src}.{key}", f"got {got}, want {want}")


def compare_event_records(go_events: list[dict], py_events: list[dict], model, full: bool, path: str) -> None:
    if len(go_events) != len(py_events):
        fail(path, f"events len got {len(go_events)} want {len(py_events)}")
    for i, (g, p) in enumerate(zip(go_events, py_events)):
        q = f"{path}[{i}]"
        for key in ("step", "event_class"):
            if g[key] != p[key]:
                fail(q + "." + key, f"got {g[key]!r} want {p[key]!r}")
        scalar_wire_matches(g["exact_dt"], p["exact_dt"], model, q + ".exact_dt")
        scalar_wire_matches(g["exact_T"], p["exact_T"], model, q + ".exact_T")
        if len(g["batch"]) != len(p["batch"]):
            fail(q + ".batch", f"length got {len(g['batch'])} want {len(p['batch'])}")
        for j, (gb, pb) in enumerate(zip(g["batch"], p["batch"])):
            r = f"{q}.batch[{j}]"
            for key in ("kind", "bodies", "face", "wall"):
                if gb[key] != pb[key]:
                    fail(r + "." + key, f"got {gb[key]!r} want {pb[key]!r}")
            scalar_wire_matches(gb["dt"], pb["dt"], model, r + ".dt")
        if full:
            # Initial time-zero record has no pre-state; all subsequent rows do.
            if "pre_state" in p:
                if len(g.get("pre_state", [])) != len(p["pre_state"]):
                    fail(q + ".pre_state", "missing or wrong length")
                for j, (gb, pb) in enumerate(zip(g["pre_state"], p["pre_state"])):
                    body_matches(gb, _body_from_python_wire(model, pb), f"{q}.pre_state[{j}]")
            if "post_state" in p:
                if len(g.get("post_state", [])) != len(p["post_state"]):
                    fail(q + ".post_state", "missing or wrong length")
                for j, (gb, pb) in enumerate(zip(g["post_state"], p["post_state"])):
                    body_matches(gb, _body_from_python_wire(model, pb), f"{q}.post_state[{j}]")
            if "metrics" in p and g.get("metrics") is not None:
                compare_metrics(g["metrics"], p["metrics"], q + ".metrics")


def _body_from_python_wire(model, wire: dict):
    f = model.field
    compact_names = {1: ("a",), 2: ("a", "b"), 4: ("a", "b", "c", "d")}[f.dimension]
    def scalar(w):
        return E(f, tuple(Fraction(w[name]) for name in compact_names))
    p = wire["position"]
    v = wire["velocity"]
    return Body(Vec(scalar(p["x"]), scalar(p["y"])), Vec(scalar(v["x"]), scalar(v["y"])))


def next_batch_independent(model, container, bodies):
    """Independent Python batch classifier matching the declared v2 contract."""
    events = []
    for i in range(len(bodies)):
        events.extend(pycore._wall_candidates(model, container, bodies, i))
    for i, j in combinations(range(len(bodies)), 2):
        event = pycore._pair_candidate(model, bodies, i, j)
        if event is not None:
            events.append(event)
    if not events:
        return None
    dt = events[0].dt
    for event in events[1:]:
        if event.dt < dt:
            dt = event.dt
    batch = [event for event in events if (event.dt - dt).sign() == 0]
    if any(event.kind == "PAIR_CORNER" for event in batch):
        return batch, "PAIR_CORNER"
    wall_bodies = [event.bodies[0] for event in batch if event.kind == "WALL_FACE"]
    if len(wall_bodies) != len(set(wall_bodies)):
        return batch, "WALL_CORNER"
    if len(batch) == 1:
        return batch, "REGULAR"
    involved = [body for event in batch for body in event.bodies]
    if len(involved) == len(set(involved)):
        if all(event.kind == "WALL_FACE" for event in batch):
            return batch, "INDEPENDENT_WALL_BATCH"
        return batch, "INDEPENDENT_BATCH"
    return batch, "COUPLED_SIMULTANEOUS"


def run_independent(model, container, start, cap, initial_records=None):
    """Fresh Python replay loop; it does not invoke Go or the legacy run()."""
    bodies = [b.copy() for b in start]
    elapsed = model.field.zero()
    records = list(initial_records or [])
    seen = {pycore.state_key(bodies): 0}
    initial_metrics = pycore.state_metrics(bodies)
    high_metrics = pycore.state_metrics(bodies)
    time_metrics = pycore._metric_group([elapsed])
    first_denominator_promotion = None
    first_height_growth = None
    pair_faces = [r["face"] for r in records if r.get("kind") == "PAIR_FACE" and r.get("face") is not None]
    for step in range(1, cap + 1):
        upcoming = next_batch_independent(model, container, bodies)
        if upcoming is None:
            return pycore._outcome("NO_EVENT", step - 1, elapsed, records, bodies, seen, pair_faces,
                                   initial_metrics, high_metrics, time_metrics,
                                   first_denominator_promotion, first_height_growth)
        batch, event_class = upcoming
        dt = batch[0].dt
        pre_hash = pycore.state_hash(bodies)
        pre_state = [b.wire() for b in bodies]
        pycore.advance(bodies, dt)
        elapsed = elapsed + dt
        time_metrics = pycore._metric_group([elapsed])
        batch_wire = [event.wire() for event in batch]
        if event_class not in ("REGULAR", "INDEPENDENT_WALL_BATCH", "INDEPENDENT_BATCH"):
            records.append({"step": step, "exact_dt": dt.wire(), "exact_T": elapsed.wire(),
                            "event_class": event_class, "batch": batch_wire,
                            "pre_state_hash": pre_hash, "post_state_hash": None,
                            "pre_state": pre_state,
                            "post_state": [b.wire() for b in bodies]})
            return pycore._outcome(event_class, step, elapsed, records, bodies, seen, pair_faces,
                                   initial_metrics, high_metrics, time_metrics,
                                   first_denominator_promotion, first_height_growth)
        for event in batch:
            pycore.resolve_event(model, bodies, event)
            if event.kind == "PAIR_FACE" and event.face is not None:
                pair_faces.append(event.face)
        metrics = pycore.state_metrics(bodies)
        high_metrics = pycore._merge_metrics(high_metrics, metrics)
        if first_denominator_promotion is None and metrics["all_coordinates"]["max_denominator"] > initial_metrics["all_coordinates"]["max_denominator"]:
            first_denominator_promotion = step
        if first_height_growth is None and metrics["all_coordinates"]["max_abs_numerator"] > initial_metrics["all_coordinates"]["max_abs_numerator"]:
            first_height_growth = step
        key = pycore.state_key(bodies)
        post_hash = pycore.state_hash(bodies)
        records.append({"step": step, "exact_dt": dt.wire(), "exact_T": elapsed.wire(),
                        "event_class": event_class, "batch": batch_wire,
                        "pre_state_hash": pre_hash, "post_state_hash": post_hash,
                        "pre_state": pre_state,
                        "post_state": [b.wire() for b in bodies], "metrics": metrics})
        if key in seen:
            out = pycore._outcome("RETURN", step, elapsed, records, bodies, seen, pair_faces,
                                  initial_metrics, high_metrics, time_metrics,
                                  first_denominator_promotion, first_height_growth)
            out["preperiod_events"] = seen[key]
            out["period_events"] = step - seen[key]
            out["cycle_T"] = elapsed.wire()
            return out
        seen[key] = step
    return pycore._outcome("CAP", cap, elapsed, records, bodies, seen, pair_faces,
                           initial_metrics, high_metrics, time_metrics,
                           first_denominator_promotion, first_height_growth)


def py_lattice_outcome(model, L: int, start: dict, cap: int):
    sites = lattice_sites(model, L); vels = cardinal_velocities(model.field)
    bodies = [Body(sites[i], vels[n]) for i, n in zip(start["sites"], start["velocities"])]
    return run_independent(model, make_container(model, L), bodies, cap)


def py_centered_outcome(model, L: int, start: dict, cap: int):
    bodies, rec = centered_pair_start(model, L, start["face"], *start["incoming"])
    return run_independent(model, make_container(model, L), bodies, cap, initial_records=[rec])


def _scalar_from_go_common_wire(model, wire: dict):
    # Go always emits a,b,c,d for 1,sqrt2,sqrt3,sqrt6.  The legacy Python
    # model retains only the masks appropriate to its exact subfield.
    global_names = {0: "a", 1: "b", 2: "c", 3: "d"}
    return E(model.field, tuple(Fraction(wire[global_names[mask]]) for mask in model.field.basis_masks))


def _body_from_go_common_wire(model, wire: dict):
    p, v = wire["position"], wire["velocity"]
    return Body(
        Vec(_scalar_from_go_common_wire(model, p["x"]), _scalar_from_go_common_wire(model, p["y"])),
        Vec(_scalar_from_go_common_wire(model, v["x"]), _scalar_from_go_common_wire(model, v["y"])),
    )


def py_explicit_state_outcome(model, L: int, state: list[dict], cap: int):
    bodies = [_body_from_go_common_wire(model, b) for b in state]
    return run_independent(model, make_container(model, L), bodies, cap)


def compare_outcome(go: dict, py: dict, model, full: bool, path: str) -> None:
    for key in ("status", "event_batches", "distinct_states", "pair_face_word"):
        if go[key] != py[key]:
            fail(path + "." + key, f"got {go[key]!r}, want {py[key]!r}")
    scalar_wire_matches(go["exact_T"], py["exact_T"], model, path + ".exact_T")
    compare_event_records(go.get("events", []), py["events"], model, full, path + ".events")
    compare_metrics(go["initial_metrics"], py["initial_metrics"], path + ".initial_metrics")
    compare_metrics(go["final_metrics"], py["final_metrics"], path + ".final_metrics")
    compare_metrics(go["max_metrics"], py["max_metrics"], path + ".max_metrics")
    if full:
        if len(go["final_state"]) != len(py["final_state"]):
            fail(path + ".final_state", "wrong length")
        for i, (gb, pb) in enumerate(zip(go["final_state"], py["final_state"])):
            body_matches(gb, _body_from_python_wire(model, pb), f"{path}.final_state[{i}]")


def check_atlas(doc: dict) -> dict:
    model = model_for(doc["model"]["model_id"])
    L = doc["container"]["cells_per_side"]
    cap = doc["event_cap"]
    counts: dict[str, int] = {}
    for i, case in enumerate(doc["results"]):
        start = case["start"]
        if "sites" in start:
            py = py_lattice_outcome(model, L, start, cap)
        else:
            py = py_centered_outcome(model, L, start, cap)
        compare_outcome(case["outcome"], py, model, False, f"results[{i}]")
        counts[py["status"]] = counts.get(py["status"], 0) + 1
    if counts != doc["counts"]:
        fail("counts", f"got {doc['counts']}, recomputed {counts}")
    return {"kind": "atlas", "checked_cases": len(doc["results"]), "counts": counts, "result": "PASS"}


def _replay_instance(doc: dict):
    model = model_for(doc["model"]["model_id"])
    L = doc["container"]["cells_per_side"]
    cap = doc["stopping_rule"]["event_cap"]
    inst = doc["instance"]
    if "sites" in inst:
        py = py_lattice_outcome(model, L, inst, cap)
    elif "initial_state" in inst:
        py = py_explicit_state_outcome(model, L, inst["initial_state"], cap)
    else:
        py = py_centered_outcome(model, L, inst, cap)
    return model, py


def check_certificate(doc: dict) -> dict:
    model, py = _replay_instance(doc)
    compare_outcome(doc["result"], py, model, True, "result")
    return {"kind": "certificate", "certificate_id": doc["certificate_id"], "checked_batches": py["event_batches"], "status": py["status"], "result": "PASS"}


def check_compact_checkpoint(doc: dict) -> dict:
    model, py = _replay_instance(doc)
    compare_outcome(doc["result"], py, model, False, "result")
    final = doc["result"].get("final_state", [])
    if len(final) != len(py["final_state"]):
        fail("result.final_state", "wrong length")
    for i, (g, p) in enumerate(zip(final, py["final_state"])):
        body_matches(g, _body_from_python_wire(model, p), f"result.final_state[{i}]")
    return {"kind": "compact_checkpoint", "checkpoint_id": doc["checkpoint_id"], "checked_batches": py["event_batches"], "status": py["status"], "result": "PASS"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ns = ap.parse_args()
    doc = json.loads(ns.input.read_text())
    schema = doc.get("schema", "")
    if schema.startswith("lattice-chaos-atlas/") or schema.startswith("lattice-chaos-centered-atlas/"):
        report = check_atlas(doc)
    elif schema.startswith("lattice-chaos-self-contained-certificate/"):
        report = check_certificate(doc)
    elif schema.startswith("lattice-chaos-compact-progress/"):
        report = check_compact_checkpoint(doc)
    else:
        raise SystemExit(f"unsupported schema {schema}")
    report["source"] = str(ns.input)
    ns.out.parent.mkdir(parents=True, exist_ok=True)
    ns.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
