#!/usr/bin/env python3
"""Check Artifact 18 compact-block coverage, linkage, and optionally each block."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tarfile
from pathlib import Path

LANES = ("d12", "24A", "24B")


def member_json(archive: tarfile.TarFile, suffix: str) -> dict:
    names = [name for name in archive.getnames() if name.endswith(suffix)]
    if len(names) != 1:
        raise ValueError(f"expected one {suffix}, found {len(names)}")
    member = archive.extractfile(names[0])
    if member is None:
        raise ValueError(f"cannot read {suffix}")
    return json.load(member)


def block_record(path: Path) -> dict:
    with tarfile.open(path, "r:gz") as archive:
        block = member_json(archive, "/BLOCK.json")
        start_state = member_json(archive, "/start_state.json")
        end_state = member_json(archive, "/end_state.json")
    return {"path": path, "block": block, "start_state": start_state, "end_state": end_state}


def canonical_state(state: dict) -> dict:
    return {key: state[key] for key in ("step", "exact_T", "state")}


def validate_lane(root: Path, lane: str, target: int) -> tuple[int, list[dict]]:
    records = [block_record(path) for path in (root / "blocks" / lane).glob("*.block.tar.gz")]
    records.sort(key=lambda item: int(item["block"]["start"]["step"]))
    expected = 0
    previous_end: dict | None = None
    for record in records:
        block = record["block"]
        start = int(block["start"]["step"])
        end = int(block["end"]["step"])
        if block.get("schema") != "exact-two-body-compact-block/v3":
            raise ValueError(f"{lane}: unsupported schema in {record['path'].name}")
        if int(block["events"]) != end - start:
            raise ValueError(f"{lane}: event span mismatch in {record['path'].name}")
        if start != expected:
            raise ValueError(f"{lane}: expected start {expected}, got {start} in {record['path'].name}")
        if int(record["start_state"]["step"]) != start or int(record["end_state"]["step"]) != end:
            raise ValueError(f"{lane}: state step mismatch in {record['path'].name}")
        if previous_end is not None and canonical_state(record["start_state"]) != canonical_state(previous_end):
            raise ValueError(f"{lane}: decoded end/start state mismatch before {record['path'].name}")
        previous_end = record["end_state"]
        expected = end
    if expected != target:
        raise ValueError(f"{lane}: coverage ends at {expected}, expected {target}")
    return expected, records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--target", type=int, default=50_000)
    parser.add_argument("--full", action="store_true", help="run the per-block structural/checksum verifier")
    args = parser.parse_args()
    root = args.root.resolve()
    checker = Path(__file__).resolve().parent / "check_compact_block.py"
    all_records: list[dict] = []
    for lane in LANES:
        coverage, records = validate_lane(root, lane, args.target)
        all_records.extend(records)
        print(f"PASS {lane}: {len(records)} compact blocks, coverage 1..{coverage}")
    if args.full:
        for index, record in enumerate(all_records, 1):
            result = subprocess.run([sys.executable, str(checker), str(record["path"])], text=True, capture_output=True)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)
            print(f"[{index}/{len(all_records)}] {result.stdout.strip()}")
    print(f"PASS Artifact 18 corpus: {len(all_records)} blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
