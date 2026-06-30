#!/usr/bin/env python3
"""Derive only read-only sequence and D4 metadata from Go-produced records."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"

COORD = {0: (-1, -1), 1: (1, -1), 2: (-1, 1), 3: (1, 1)}
INV_COORD = {v: k for k, v in COORD.items()}
VEC = {"E": (1, 0), "W": (-1, 0), "N": (0, 1), "S": (0, -1)}
INV_VEC = {v: k for k, v in VEC.items()}
NEG = {"E": "W", "W": "E", "N": "S", "S": "N"}

# All D4 maps in a stable listing.  They act on both centroid sites and velocities.
D4 = [
    ("id", lambda x,y: (x,y)),
    ("r90", lambda x,y: (-y,x)),
    ("r180", lambda x,y: (-x,-y)),
    ("r270", lambda x,y: (y,-x)),
    ("mx", lambda x,y: (-x,y)),
    ("diag", lambda x,y: (y,x)),
    ("my", lambda x,y: (x,-y)),
    ("anti_diag", lambda x,y: (-y,-x)),
]

def canonical_lattice_start(sites: list[int], velocities: list[str]) -> tuple[tuple[int,str], ...]:
    images = []
    for _, f in D4:
        transformed = []
        for site, velocity in zip(sites, velocities):
            transformed.append((INV_COORD[f(*COORD[site])], INV_VEC[f(*VEC[velocity])]))
        images.append(tuple(sorted(transformed)))  # bodies are identical
    return min(images)

def raw_lattice_key(sites: list[int], velocities: list[str]) -> tuple[tuple[int,str], ...]:
    return tuple(sorted(zip(sites, velocities)))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def d4_audit(path: Path, label: str) -> dict:
    doc = json.loads(path.read_text())
    caps = [r for r in doc["results"] if r["outcome"]["status"] == "CAP"]
    by_rep: dict[tuple, list[dict]] = defaultdict(list)
    raw: dict[tuple, dict] = {}
    for row in caps:
        st = row["start"]
        rep = canonical_lattice_start(st["sites"], st["velocities"])
        by_rep[rep].append(row)
        raw[raw_lattice_key(st["sites"], st["velocities"])] = row
    classes = []
    for rep in sorted(by_rep):
        members = by_rep[rep]
        exemplar = min(members, key=lambda r: r["raw_start_id"])
        st = exemplar["start"]
        reversed_key = raw_lattice_key(st["sites"], [NEG[v] for v in st["velocities"]])
        reversed_row = raw.get(reversed_key)
        classes.append({
            "representative": [{"site": s, "velocity": v} for s,v in rep],
            "earliest_case_id": exemplar["case_id"],
            "raw_member_count": len(members),
            "members": [r["case_id"] for r in members],
            "time_reverse_same_sites": None if reversed_row is None else reversed_row["case_id"],
        })
    return {
        "family": label,
        "source": str(path.relative_to(ROOT)),
        "source_sha256": sha(path),
        "raw_cap_cases": len(caps),
        "D4_classes": classes,
    }

def centered_lexmin() -> dict:
    path = DATA / "dodecagon_centered" / "atlas_all_faces_cap500.json"
    doc = json.loads(path.read_text())
    caps = []
    for row in doc["results"]:
        if row["outcome"]["status"] != "CAP":
            continue
        word = ''.join(str(face % 3) for face in row["outcome"]["pair_face_word"])
        caps.append((word, row["raw_start_id"], row))
    caps.sort(key=lambda x: (x[0], x[1]))
    word, _, chosen = caps[0]
    classes = defaultdict(list)
    for w, _, r in caps:
        classes[w].append(r["case_id"])
    return {
        "source": str(path.relative_to(ROOT)),
        "source_sha256": sha(path),
        "reduction": "every pair face label reduced modulo 3; the prescribed time-zero central contact is included",
        "raw_cap_cases": len(caps),
        "distinct_ternary_words": len(classes),
        "lexicographically_minimal": {
            "case_id": chosen["case_id"],
            "face": chosen["start"]["face"],
            "incoming": chosen["start"]["incoming"],
            "word_500": word,
            "equivalent_raw_cases_with_same_word": classes[word],
        },
        "all_distinct_words": [{"word": w, "raw_cases": rows} for w, rows in sorted(classes.items())],
    }

def write_face_sequence(cert: Path, stem: str) -> dict:
    doc = json.loads(cert.read_text())
    faces = doc["result"]["pair_face_word"]
    outdir = DATA / "dodecagon_centered" / "ternary"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / f"{stem}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pair_contact_index", "face_label", "ternary_face_class_mod_3"])
        for i, face in enumerate(faces):
            writer.writerow([i, face, face % 3])
    txt_path = outdir / f"{stem}.txt"
    txt_path.write_text(",".join(str(f % 3) for f in faces) + "\n")
    return {
        "certificate": str(cert.relative_to(ROOT)),
        "certificate_sha256": sha(cert),
        "pair_contacts": len(faces),
        "reduction": "face_label modulo 3, with time-zero face contact at index 0",
        "csv": str(csv_path.relative_to(ROOT)),
        "text": str(txt_path.relative_to(ROOT)),
        "prefix_120": "".join(str(f % 3) for f in faces[:120]),
        "last_120": "".join(str(f % 3) for f in faces[-120:]),
    }


def reverse_stem() -> dict:
    path = DATA / "dodecagon_centered" / "certificates" / "centered_dodecagon_f1_EN_reverse_stem.json"
    doc = json.loads(path.read_text())
    source = doc["instance"]["source_centered_contact"]
    rows = [{
        "reverse_time_event_index": 0,
        "physical_role": "source central face contact at reverse-time zero",
        "event_class": "INITIAL_PAIR_FACE",
        "face_label": source["face"],
        "ternary_face_class_mod_3": source["face"] % 3,
        "emits_regular_ternary_symbol": True,
        "exact_reverse_time": {"a": "0", "b": "0", "c": "0", "d": "0"},
    }]
    for rec in doc["evolution"]["events"]:
        b = rec["batch"][0]
        rows.append({
            "reverse_time_event_index": rec["step"],
            "physical_role": "negative-physical-time continuation from resolved centered contact",
            "event_class": rec["event_class"],
            "kind": b["kind"],
            "face_label": b["face"],
            "wall": b["wall"],
            "ternary_face_class_mod_3": None,
            "emits_regular_ternary_symbol": False,
            "exact_reverse_time": rec["exact_T"],
        })
    outdir = DATA / "dodecagon_centered" / "ternary"
    csv_path = outdir / "centered_dodecagon_f1_EN_reverse_stem.csv"
    cols = ["reverse_time_event_index", "physical_role", "event_class", "kind", "face_label", "wall", "ternary_face_class_mod_3", "emits_regular_ternary_symbol", "exact_reverse_time"]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            packed = dict(row)
            packed["exact_reverse_time"] = json.dumps(packed["exact_reverse_time"], sort_keys=True)
            w.writerow(packed)
    txt_path = outdir / "centered_dodecagon_f1_EN_reverse_stem.txt"
    txt_path.write_text("1\n")
    return {
        "certificate": str(path.relative_to(ROOT)),
        "certificate_sha256": sha(path),
        "csv": str(csv_path.relative_to(ROOT)),
        "text": str(txt_path.relative_to(ROOT)),
        "regular_ternary_word": "1",
        "terminal_status": doc["result"]["status"],
        "terminal_batches_after_t0": doc["result"]["event_batches"],
        "events": rows,
        "interpretation": "The true past branch from the resolved t=0 state has only the source trit 1; it then has two wall contacts and reaches a pair-corner terminal. Wall contacts and the terminal corner emit no regular ternary digit.",
    }


def dodeca_sequences() -> dict:
    full = DATA / "dodecagon_centered" / "certificates" / "centered_dodecagon_f1_EN_cap2000.json"
    deep = DATA / "dodecagon_centered" / "centered_dodecagon_f1_EN_cap7500_compact.json"
    return {
        "full_cap2000": write_face_sequence(full, "centered_dodecagon_f1_EN_cap2000"),
        "compact_cap7500": write_face_sequence(deep, "centered_dodecagon_f1_EN_cap7500"),
        "reverse_stem": reverse_stem(),
    }

def main() -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "lattice-chaos-derived-symmetry-and-sequences/v1",
        "24gon_L2_N2": d4_audit(DATA / "24gon_L2_N2" / "atlas.json", "24gon_L2_N2"),
        "octagon_L2_N3": d4_audit(DATA / "octagon_L2_N3" / "atlas.json", "octagon_L2_N3"),
        "dodecagon_centered": centered_lexmin(),
        "dodecagon_sequences": dodeca_sequences(),
    }
    path = ANALYSIS / "symmetry_and_sequence_audit.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(path)
    print(json.dumps({
        "24gon_D4_classes": len(report["24gon_L2_N2"]["D4_classes"]),
        "octagon_D4_classes": len(report["octagon_L2_N3"]["D4_classes"]),
        "dodecagon_lexmin": report["dodecagon_centered"]["lexicographically_minimal"]["case_id"],
        "dodecagon_ternary_contacts": report["dodecagon_sequences"]["full_cap2000"]["pair_contacts"],
    }, indent=2))

if __name__ == "__main__":
    main()
