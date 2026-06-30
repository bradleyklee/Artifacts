"""Generic exact fixed-orientation regular-polygon billiard evolver."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, product
from fractions import Fraction
from hashlib import sha256
from typing import Iterable, Sequence

from .exact import E, Field, Q, Q2, Q3, Q23, exact_max


@dataclass(frozen=True)
class Vec:
    x: E
    y: E

    def __add__(self, other: "Vec") -> "Vec": return Vec(self.x + other.x, self.y + other.y)
    def __sub__(self, other: "Vec") -> "Vec": return Vec(self.x - other.x, self.y - other.y)
    def scale(self, scalar: E | int | Fraction) -> "Vec": return Vec(self.x * scalar, self.y * scalar)
    def key(self) -> str: return f"{self.x.key()},{self.y.key()}"
    def wire(self) -> dict[str, dict[str, str]]: return {"x": self.x.wire(), "y": self.y.wire()}


def dot(a: Vec, b: Vec) -> E:
    return a.x * b.x + a.y * b.y


CARDINAL_NAMES = ("E", "W", "N", "S")


def cardinal_velocities(field: Field) -> dict[str, Vec]:
    z, one = field.zero(), field.one()
    return {"E": Vec(one, z), "W": Vec(-one, z), "N": Vec(z, one), "S": Vec(z, -one)}


@dataclass(frozen=True)
class PolygonModel:
    model_id: str
    sides: int
    edge: E
    apothem: E
    field: Field
    normals: tuple[Vec, ...]

    @property
    def cell_side(self) -> E:
        # cardinal width is 2*apothem = cell_side/2
        return self.apothem * 4

    @property
    def cardinal_faces(self) -> tuple[int, ...]:
        stride = self.sides // 4
        return tuple(k * stride for k in range(4))

    def opposite(self, face: int) -> int:
        return (face + self.sides // 2) % self.sides

    def normal_label_degrees(self, face: int) -> str:
        return str(Fraction(360 * face, self.sides))

    def wire(self) -> dict:
        return {
            "model_id": self.model_id,
            "polygon": f"regular {self.sides}-gon",
            "sides": self.sides,
            "edge": self.edge.wire(),
            "apothem": self.apothem.wire(),
            "cell_side": self.cell_side.wire(),
            "cardinal_width": (self.apothem * 2).wire(),
            "field": self.field.name,
            "normal_label": "face k has normal angle 360*k/sides degrees",
            "geometry_version": "unified-v1",
        }


def model_for(shape: str) -> PolygonModel:
    shape = shape.lower().replace("-", "")
    if shape in ("square", "4gon", "4"):
        field, sides = Q, 4
    elif shape in ("octagon", "8gon", "8"):
        field, sides = Q2, 8
    elif shape in ("dodecagon", "12gon", "12"):
        field, sides = Q3, 12
    elif shape in ("24gon", "icositetragon", "24"):
        field, sides = Q23, 24
    else:
        raise ValueError(f"unknown shape: {shape}")
    return _build_regular_model(field, sides)


def _build_regular_model(field: Field, sides: int) -> PolygonModel:
    q, z = field.q, field.zero()
    s2 = field.sqrt(2) if field in (Q2, Q23) else None
    s3 = field.sqrt(3) if field in (Q3, Q23) else None
    if sides == 4:
        normals = (Vec(q(1), z), Vec(z, q(1)), Vec(q(-1), z), Vec(z, q(-1)))
        apothem = q(1, 4)  # edge=1/2
        name = "square"
    elif sides == 8:
        assert s2 is not None
        h = s2 / 2
        normals = (Vec(q(1), z), Vec(h, h), Vec(z, q(1)), Vec(-h, h),
                   Vec(q(-1), z), Vec(-h, -h), Vec(z, q(-1)), Vec(h, -h))
        apothem = (q(1) + s2) / 4
        name = "octagon"
    elif sides == 12:
        assert s3 is not None
        h = s3 / 2
        normals = (Vec(q(1), z), Vec(h, q(1, 2)), Vec(q(1, 2), h), Vec(z, q(1)),
                   Vec(q(-1, 2), h), Vec(-h, q(1, 2)), Vec(q(-1), z),
                   Vec(-h, q(-1, 2)), Vec(q(-1, 2), -h), Vec(z, q(-1)),
                   Vec(q(1, 2), -h), Vec(h, q(-1, 2)))
        apothem = (q(2) + s3) / 4
        name = "dodecagon"
    elif sides == 24:
        assert s2 is not None and s3 is not None
        s6 = s2 * s3
        c15, ss15 = (s6 + s2) / 4, (s6 - s2) / 4
        c30, ss30 = s3 / 2, q(1, 2)
        c45, ss45 = s2 / 2, s2 / 2
        c60, ss60 = q(1, 2), s3 / 2
        c75, ss75 = (s6 - s2) / 4, (s6 + s2) / 4
        base = ((q(1), z), (c15, ss15), (c30, ss30), (c45, ss45),
                (c60, ss60), (c75, ss75), (z, q(1)))
        ns: list[Vec] = []
        for k in range(24):
            if k <= 6: x, y = base[k]
            elif k <= 12: x, y = -base[12 - k][0], base[12 - k][1]
            elif k <= 18: x, y = -base[k - 12][0], -base[k - 12][1]
            else: x, y = base[24 - k][0], -base[24 - k][1]
            ns.append(Vec(x, y))
        normals = tuple(ns)
        # edge=1/2; a=e/(2tan(pi/24)) = 1/(4tan 7.5deg)
        tan75 = ss15 / (q(1) + c15)
        apothem = q(1, 4) / tan75
        name = "24gon"
    else:
        raise ValueError("only 4,8,12,24 are supported")
    return PolygonModel(name, sides, q(1, 2), apothem, field, normals)


@dataclass
class Body:
    pos: Vec
    vel: Vec

    def copy(self) -> "Body": return Body(self.pos, self.vel)
    def key(self) -> str: return f"{self.pos.key()}@{self.vel.key()}"
    def wire(self) -> dict: return {"position": self.pos.wire(), "velocity": self.vel.wire()}


@dataclass(frozen=True)
class Event:
    dt: E
    kind: str  # PAIR_FACE, PAIR_CORNER, WALL_FACE
    bodies: tuple[int, ...]
    face: int | None = None
    wall: str | None = None

    def wire(self) -> dict:
        return {"dt": self.dt.wire(), "kind": self.kind, "bodies": list(self.bodies),
                "face": self.face, "wall": self.wall}


@dataclass(frozen=True)
class Container:
    cells_per_side: int
    half_side: E

    def wire(self) -> dict:
        return {"kind": "axis_aligned_square", "cells_per_side": self.cells_per_side,
                "half_side": self.half_side.wire()}


def make_container(model: PolygonModel, cells_per_side: int) -> Container:
    if cells_per_side < 2:
        raise ValueError("the declared search family begins at L=2")
    return Container(cells_per_side, model.cell_side * Fraction(cells_per_side, 2))


def lattice_sites(model: PolygonModel, cells_per_side: int) -> list[Vec]:
    d = model.cell_side
    return [Vec(d * Fraction(2 * x + 1 - cells_per_side, 2),
                d * Fraction(2 * y + 1 - cells_per_side, 2))
            for y in range(cells_per_side) for x in range(cells_per_side)]


def _active_faces(model: PolygonModel, separation: Vec) -> list[int]:
    return [k for k, n in enumerate(model.normals)
            if (dot(n, separation) - model.apothem * 2).sign() == 0]


def _inside_difference(model: PolygonModel, separation: Vec) -> bool:
    return all((dot(n, separation) - model.apothem * 2).sign() <= 0 for n in model.normals)


def _pair_candidate(model: PolygonModel, bodies: Sequence[Body], i: int, j: int) -> Event | None:
    d = bodies[j].pos - bodies[i].pos
    rel = bodies[j].vel - bodies[i].vel
    best: tuple[E, int] | None = None
    for face, normal in enumerate(model.normals):
        derivative = dot(normal, rel)
        gap = dot(normal, d) - model.apothem * 2
        if derivative.sign() >= 0 or gap.sign() <= 0:
            continue
        dt = (-gap) / derivative
        if dt.sign() <= 0:
            continue
        loc = d + rel.scale(dt)
        if not _inside_difference(model, loc):
            continue
        if (dot(normal, loc) - model.apothem * 2).sign() != 0:
            continue
        if best is None or dt < best[0]:
            best = (dt, face)
    if best is None:
        return None
    dt, face = best
    active = _active_faces(model, d + rel.scale(dt))
    kind = "PAIR_FACE" if len(active) == 1 else "PAIR_CORNER"
    return Event(dt, kind, (i, j), face=face)


def _wall_candidates(model: PolygonModel, container: Container, bodies: Sequence[Body], i: int) -> list[Event]:
    body = bodies[i]
    q = model.field.q
    out: list[Event] = []
    for coord, velocity, direction, sign in ((body.pos.x, body.vel.x, "E", 1),
                                             (body.pos.x, body.vel.x, "W", -1),
                                             (body.pos.y, body.vel.y, "N", 1),
                                             (body.pos.y, body.vel.y, "S", -1)):
        target = container.half_side - model.apothem if sign > 0 else -container.half_side + model.apothem
        speed = velocity if sign > 0 else -velocity
        gap = target - coord if sign > 0 else coord - target
        if speed.sign() > 0 and gap.sign() > 0:
            out.append(Event(gap / speed, "WALL_FACE", (i,), wall=direction))
    return out


def next_batch(model: PolygonModel, container: Container, bodies: Sequence[Body]) -> tuple[list[Event], str] | None:
    events: list[Event] = []
    for i in range(len(bodies)):
        events.extend(_wall_candidates(model, container, bodies, i))
    for i, j in combinations(range(len(bodies)), 2):
        event = _pair_candidate(model, bodies, i, j)
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
    if all(event.kind == "WALL_FACE" for event in batch):
        return batch, "INDEPENDENT_WALL_BATCH"
    return batch, "COUPLED_SIMULTANEOUS"


def advance(bodies: Sequence[Body], dt: E) -> None:
    for body in bodies:
        body.pos = body.pos + body.vel.scale(dt)


def resolve_event(model: PolygonModel, bodies: Sequence[Body], event: Event) -> None:
    if event.kind == "WALL_FACE":
        i = event.bodies[0]
        b = bodies[i]
        if event.wall in ("E", "W"):
            b.vel = Vec(-b.vel.x, b.vel.y)
        else:
            b.vel = Vec(b.vel.x, -b.vel.y)
        return
    if event.kind != "PAIR_FACE" or event.face is None:
        raise ValueError(f"cannot resolve {event.kind}")
    i, j = event.bodies
    a, b = bodies[i], bodies[j]
    n = model.normals[event.face]
    g = dot(n, b.vel - a.vel)
    a.vel = a.vel + n.scale(g)
    b.vel = b.vel - n.scale(g)


def state_key(bodies: Sequence[Body]) -> str:
    return "|".join(body.key() for body in bodies)


def state_hash(bodies: Sequence[Body]) -> str:
    return sha256(state_key(bodies).encode("ascii")).hexdigest()


def _metric_group(values: Sequence[E]) -> dict[str, int]:
    num, den = exact_max(values)
    return {"max_abs_numerator": num, "max_denominator": den,
            "max_numerator_bits": num.bit_length(), "max_denominator_bits": den.bit_length()}


def state_metrics(bodies: Sequence[Body]) -> dict[str, dict[str, int]]:
    positions = [coordinate for body in bodies for coordinate in (body.pos.x, body.pos.y)]
    velocities = [coordinate for body in bodies for coordinate in (body.vel.x, body.vel.y)]
    return {"positions": _metric_group(positions), "velocities": _metric_group(velocities),
            "all_coordinates": _metric_group(positions + velocities)}


def _merge_metrics(left: dict[str, dict[str, int]], right: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    return {group: {metric: max(left[group][metric], right[group][metric]) for metric in left[group]}
            for group in left}


def run(model: PolygonModel, container: Container, start: Sequence[Body], cap: int,
        initial_records: list[dict] | None = None) -> dict:
    bodies = [b.copy() for b in start]
    elapsed = model.field.zero()
    records: list[dict] = list(initial_records or [])
    seen: dict[str, int] = {state_key(bodies): 0}
    initial_metrics = state_metrics(bodies)
    high_metrics = state_metrics(bodies)
    time_metrics = _metric_group([elapsed])
    first_denominator_promotion: int | None = None
    first_height_growth: int | None = None
    pair_faces: list[int] = [r["face"] for r in records if r.get("kind") == "PAIR_FACE" and r.get("face") is not None]

    for step in range(1, cap + 1):
        upcoming = next_batch(model, container, bodies)
        if upcoming is None:
            return _outcome("NO_EVENT", step - 1, elapsed, records, bodies, seen, pair_faces,
                            initial_metrics, high_metrics, time_metrics, first_denominator_promotion, first_height_growth)
        batch, event_class = upcoming
        dt = batch[0].dt
        pre_hash = state_hash(bodies)
        advance(bodies, dt)
        elapsed = elapsed + dt
        time_metrics = _metric_group([elapsed])
        batch_wire = [event.wire() for event in batch]
        if event_class not in ("REGULAR", "INDEPENDENT_WALL_BATCH"):
            records.append({"step": step, "exact_dt": dt.wire(), "exact_T": elapsed.wire(),
                            "event_class": event_class, "batch": batch_wire,
                            "pre_state_hash": pre_hash, "post_state_hash": None,
                            "pre_state": [b.wire() for b in start] if step == 1 else None,
                            "post_state": [b.wire() for b in bodies]})
            return _outcome(event_class, step, elapsed, records, bodies, seen, pair_faces,
                            initial_metrics, high_metrics, time_metrics, first_denominator_promotion, first_height_growth)
        for event in batch:
            resolve_event(model, bodies, event)
            if event.kind == "PAIR_FACE" and event.face is not None:
                pair_faces.append(event.face)
        metrics = state_metrics(bodies)
        high_metrics = _merge_metrics(high_metrics, metrics)
        if first_denominator_promotion is None and metrics["all_coordinates"]["max_denominator"] > initial_metrics["all_coordinates"]["max_denominator"]:
            first_denominator_promotion = step
        if first_height_growth is None and metrics["all_coordinates"]["max_abs_numerator"] > initial_metrics["all_coordinates"]["max_abs_numerator"]:
            first_height_growth = step
        key = state_key(bodies)
        post_hash = state_hash(bodies)
        records.append({"step": step, "exact_dt": dt.wire(), "exact_T": elapsed.wire(),
                        "event_class": event_class, "batch": batch_wire,
                        "pre_state_hash": pre_hash, "post_state_hash": post_hash,
                        "post_state": [b.wire() for b in bodies], "metrics": metrics})
        if key in seen:
            out = _outcome("RETURN", step, elapsed, records, bodies, seen, pair_faces,
                           initial_metrics, high_metrics, time_metrics, first_denominator_promotion, first_height_growth)
            out["preperiod_events"] = seen[key]
            out["period_events"] = step - seen[key]
            out["cycle_T"] = elapsed.wire()
            return out
        seen[key] = step
    return _outcome("CAP", cap, elapsed, records, bodies, seen, pair_faces,
                    initial_metrics, high_metrics, time_metrics, first_denominator_promotion, first_height_growth)


def _outcome(status: str, steps: int, elapsed: E, records: list[dict], bodies: Sequence[Body], seen: dict[str, int],
             pair_faces: list[int], initial_metrics: dict[str, dict[str, int]], high_metrics: dict[str, dict[str, int]],
             time_metrics: dict[str, int], first_denominator_promotion: int | None, first_height_growth: int | None) -> dict:
    final_metrics = state_metrics(bodies)
    final_metrics["time"] = time_metrics
    max_metrics = dict(high_metrics)
    max_metrics["time"] = time_metrics
    return {"status": status, "event_batches": steps, "exact_T": elapsed.wire(), "events": records,
            "final_state": [b.wire() for b in bodies], "final_state_hash": state_hash(bodies),
            "distinct_states": len(seen), "pair_face_word": pair_faces,
            "initial_metrics": initial_metrics, "final_metrics": final_metrics, "max_metrics": max_metrics,
            "first_denominator_promotion": first_denominator_promotion,
            "first_numerator_height_growth": first_height_growth}


def enumerate_lattice_starts(model: PolygonModel, cells_per_side: int, bodies: int) -> Iterable[tuple[tuple[int, ...], tuple[str, ...], list[Body]]]:
    sites = lattice_sites(model, cells_per_side)
    vels = cardinal_velocities(model.field)
    for site_indices in combinations(range(len(sites)), bodies):
        for names in product(CARDINAL_NAMES, repeat=bodies):
            yield site_indices, names, [Body(sites[i], vels[name]) for i, name in zip(site_indices, names)]


def centered_pair_start(model: PolygonModel, cells_per_side: int, face: int, va: str, vb: str) -> tuple[list[Body], dict] | None:
    if not (0 <= face < model.sides):
        raise ValueError("bad face")
    velocities = cardinal_velocities(model.field)
    n = model.normals[face]
    a = model.apothem
    start = [Body(n.scale(-a), velocities[va]), Body(n.scale(a), velocities[vb])]
    g = dot(n, start[1].vel - start[0].vel)
    if g.sign() >= 0:
        return None
    contact = Event(model.field.zero(), "PAIR_FACE", (0, 1), face=face)
    resolve_event(model, start, contact)
    record = {"step": 0, "exact_dt": model.field.zero().wire(), "exact_T": model.field.zero().wire(),
              "event_class": "INITIAL_PAIR_FACE", "kind": "PAIR_FACE", "face": face,
              "batch": [contact.wire()], "post_state_hash": state_hash(start),
              "post_state": [b.wire() for b in start]}
    return start, record
