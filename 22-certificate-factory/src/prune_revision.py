#!/usr/bin/env python3
"""Stage documented superseded/generated material outside the release tree."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path("/tmp/hanna23_pruned_2026-07-31")


def size(path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.is_dir() else path.stat().st_size


def digest(path):
    if path.is_file(): return hashlib.sha256(path.read_bytes()).hexdigest()
    records = []
    for p in sorted(x for x in path.rglob("*") if x.is_file()):
        records.append((str(p.relative_to(path)), hashlib.sha256(p.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(records).encode()).hexdigest()


def main():
    targets = [ROOT / "runs/big.zip", ROOT / "runs.zip", ROOT / "work/FULL_CALCULUS_EVIDENCE_23_CASES.md", ROOT / "src/__pycache__"]
    targets += [ROOT / "runs" / f"q{i}" for i in range(2, 10)]
    targets += [ROOT / "examples" / f"q{i}" for i in (2, 4, 5)]
    targets += [ROOT / "examples/A120590/FromClaude", ROOT / "examples/A120590/FromKimi", ROOT / "examples/A120590/ReleaseCandidate"]
    q3 = ROOT / "examples/q3"
    targets += [p for p in q3.iterdir() if p.name != "ReleaseCandidate"]
    targets += [p for p in ROOT.glob("examples/A*/release/*") if p.suffix in (".aux", ".log", ".out") or p.name.endswith(".build.log")]
    targets += [p for p in ROOT.glob("release/*") if p.suffix in (".aux", ".log", ".out") or p.name.endswith(".build.log")]
    targets = sorted(set(p for p in targets if p.exists()), key=lambda p: str(p))
    if STAGE.exists():
        raise SystemExit(f"staging directory already exists: {STAGE}")
    before = size(ROOT)
    entries = []
    for source in targets:
        rel = source.relative_to(ROOT)
        entries.append({"path": str(rel), "bytes": size(source), "sha256_or_tree_sha256": digest(source)})
        destination = STAGE / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
    after = size(ROOT)
    ledger = {"date": "2026-07-31", "status": "staged_recoverably", "stage_path": str(STAGE), "project_bytes_before": before, "project_bytes_after": after, "bytes_pruned": before - after, "entries": entries}
    reports = ROOT / "reports"
    (reports / "PRUNING_LEDGER_2026-07-31.json").write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    lines = ["---", "title: Pruning ledger", "date: 2026-07-31", "---", "", "# Pruning ledger", "", f"Staged {len(entries)} paths ({before-after:,} bytes) recoverably outside the deliverable. Canonical A-number data, the four exceptional pilot runs, all concise TeX/PDF certificates, and the reviewed q=3 ReleaseCandidate were retained.", "", "| Path | Bytes | SHA-256 / tree SHA-256 |", "|---|---:|---|"]
    lines += [f"| `{x['path']}` | {x['bytes']:,} | `{x['sha256_or_tree_sha256']}` |" for x in entries]
    lines.append("")
    (reports / "PRUNING_LEDGER_2026-07-31.md").write_text("\n".join(lines))
    print(json.dumps({"paths": len(entries), "bytes_pruned": before-after, "project_bytes_after": after}))


if __name__ == "__main__":
    main()
