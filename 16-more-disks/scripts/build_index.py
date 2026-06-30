#!/usr/bin/env python3
"""Build lightweight manifests from already-produced artifact-16 records.

This script never reruns physics.  It only indexes Go outputs, independent
post-checks, derivations, and render outputs so a checker or rewrite agent can
start from a compact, explicit map of the artifact.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHECK = ROOT / "check"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def file_entry(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha(path), "bytes": path.stat().st_size}


def check_entry(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    obj = load(path)
    return {**file_entry(path), "result": obj.get("result"), "checked_batches": obj.get("checked_batches"), "checked_cases": obj.get("checked_cases"), "status": obj.get("status")}


def atlas_summary(path: Path, check_path: Path) -> dict[str, Any]:
    doc = load(path)
    return {
        "kind": "atlas",
        **file_entry(path),
        "schema": doc["schema"],
        "experiment_id": doc["experiment_id"],
        "raw_starts": doc["raw_starts"],
        "event_cap": doc["event_cap"],
        "counts": doc["counts"],
        "earliest": doc.get("earliest", {}),
        "independent_check": check_entry(check_path),
    }


def cert_summary(path: Path, check_path: Path, compact: bool = False) -> dict[str, Any]:
    doc = load(path)
    result = doc["result"]
    item = {
        "kind": "compact_checkpoint" if compact else "full_certificate",
        **file_entry(path),
        "schema": doc["schema"],
        "id": doc.get("checkpoint_id", doc.get("certificate_id")),
        "status": result["status"],
        "event_batches": result["event_batches"],
        "pair_contacts": len(result["pair_face_word"]),
        "pair_face_word_sha256": hashlib.sha256(",".join(map(str, result["pair_face_word"])).encode()).hexdigest(),
        "independent_check": check_entry(check_path),
    }
    return item


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    atlases = {
        "square_L2_N4": atlas_summary(DATA / "square_L2_N4" / "atlas.json", CHECK / "square_L2_N4.python.json"),
        "dodecagon_L2_N2": atlas_summary(DATA / "dodecagon_L2_N2" / "atlas.json", CHECK / "dodecagon_L2_N2.python.json"),
        "dodecagon_L3_N2": atlas_summary(DATA / "dodecagon_L3_N2" / "atlas.json", CHECK / "dodecagon_L3_N2.python.json"),
        "dodecagon_centered_all_faces": atlas_summary(DATA / "dodecagon_centered" / "atlas_all_faces_cap500.json", CHECK / "dodecagon_centered_all_faces.python.json"),
        "dodecagon_centered_offcardinal": atlas_summary(DATA / "dodecagon_centered" / "atlas_offcardinal_cap500.json", CHECK / "dodecagon_centered_offcardinal.python.json"),
        "24gon_L2_N2": atlas_summary(DATA / "24gon_L2_N2" / "atlas.json", CHECK / "24gon_L2_N2.python.json"),
        "octagon_L2_N3_context": atlas_summary(DATA / "octagon_L2_N3" / "atlas.json", CHECK / "octagon_L2_N3.python.json"),
    }
    certs = {
        "dodecagon_lexmin_cap500": cert_summary(DATA / "dodecagon_centered" / "certificates" / "centered_dodecagon_f1_EN_cap500.json", CHECK / "centered_dodecagon_f1_EN_cap500.python.json"),
        "dodecagon_lexmin_cap2000": cert_summary(DATA / "dodecagon_centered" / "certificates" / "centered_dodecagon_f1_EN_cap2000.json", CHECK / "centered_dodecagon_f1_EN_cap2000.python.json"),
        "dodecagon_lexmin_reverse_stem": cert_summary(DATA / "dodecagon_centered" / "certificates" / "centered_dodecagon_f1_EN_reverse_stem.json", CHECK / "centered_dodecagon_f1_EN_reverse_stem.python.json"),
        "dodecagon_lexmin_cap4000_compact": cert_summary(DATA / "dodecagon_centered" / "centered_dodecagon_f1_EN_cap4000_compact.json", CHECK / "centered_dodecagon_f1_EN_cap4000_compact.python.json", compact=True),
        "dodecagon_lexmin_cap6000_compact": cert_summary(DATA / "dodecagon_centered" / "centered_dodecagon_f1_EN_cap6000_compact.json", CHECK / "centered_dodecagon_f1_EN_cap6000_compact.python.json", compact=True),
        "dodecagon_lexmin_cap7500_compact": cert_summary(DATA / "dodecagon_centered" / "centered_dodecagon_f1_EN_cap7500_compact.json", CHECK / "centered_dodecagon_f1_EN_cap7500_compact.python.json", compact=True),
        "24gon_class_A": cert_summary(DATA / "24gon_L2_N2" / "certificates" / "24gon_L2_N2_class_A_ES_cap100.json", CHECK / "24gon_L2_N2_class_A_ES_cap100.python.json"),
        "24gon_class_B": cert_summary(DATA / "24gon_L2_N2" / "certificates" / "24gon_L2_N2_class_B_WN_cap100.json", CHECK / "24gon_L2_N2_class_B_WN_cap100.python.json"),
    }
    analysis_path = ROOT / "analysis" / "symmetry_and_sequence_audit.json"
    render_path = ROOT / "renders" / "shorts" / "render_manifest.json"
    index = {
        "schema": "artifact16-index/v1",
        "title": "Cardinal lattice polygon experiments",
        "authority": {
            "production_physics": "Go: cmd/lattice and internal/engine",
            "independent_postcheck": "Python: scripts/postcheck_go.py; does not invoke Go",
            "visuals": "Pillow/FFmpeg code renders fed only checked certificate JSON",
        },
        "finite_prefix_caveat": "CAP records are finite regular survivors, not proofs of chaos, aperiodicity, or infinitude.",
        "canonical_experiments": atlases,
        "highlighted_positive_records": certs,
        "derived_analysis": file_entry(analysis_path),
        "render_manifest": file_entry(render_path),
        "rebuild_order": [
            "make build test",
            "make scan certs deep-dodecagon",
            "make check",
            "make derive",
            "make render",
            "make index manifest package",
        ],
        "rewrite_entrypoint": "docs/REWRITE_BRIEF.md",
        "known_differences": "KNOWN_DIFFERENCES.md",
    }

    # Family-local orientation files: compact enough to navigate without opening
    # a multi-megabyte atlas.
    local = {
        DATA / "square_L2_N4" / "manifest.json": {"family": "square_L2_N4", "role": "negative control", "atlas": atlases["square_L2_N4"]},
        DATA / "dodecagon_L2_N2" / "manifest.json": {"family": "dodecagon_L2_N2", "role": "ordinary negative control", "atlas": atlases["dodecagon_L2_N2"]},
        DATA / "dodecagon_L3_N2" / "manifest.json": {"family": "dodecagon_L3_N2", "role": "ordinary negative control extension", "atlas": atlases["dodecagon_L3_N2"]},
        DATA / "dodecagon_centered" / "manifest.json": {"family": "dodecagon_centered", "role": "special positive seed family", "atlases": [atlases["dodecagon_centered_all_faces"], atlases["dodecagon_centered_offcardinal"]], "certificates": [certs["dodecagon_lexmin_cap500"], certs["dodecagon_lexmin_cap2000"], certs["dodecagon_lexmin_reverse_stem"], certs["dodecagon_lexmin_cap4000_compact"], certs["dodecagon_lexmin_cap6000_compact"], certs["dodecagon_lexmin_cap7500_compact"]]},
        DATA / "24gon_L2_N2" / "manifest.json": {"family": "24gon_L2_N2", "role": "ordinary positive two-body family", "atlas": atlases["24gon_L2_N2"], "certificates": [certs["24gon_class_A"], certs["24gon_class_B"]]},
        DATA / "octagon_L2_N3" / "manifest.json": {"family": "octagon_L2_N3", "role": "context-only early three-body survivor atlas", "atlas": atlases["octagon_L2_N3_context"]},
    }
    for p, value in local.items():
        write_json(p, {"schema": "artifact16-family-manifest/v1", **value})
    write_json(ROOT / "MANIFEST.json", index)
    write_json(ROOT / "index.json", index)
    print(ROOT / "MANIFEST.json")


if __name__ == "__main__":
    main()
