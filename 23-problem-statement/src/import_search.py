#!/usr/bin/env python3
"""Import checkpoint JSONL files without overwriting local files."""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if source.name != "search" and (source / "search").is_dir():
        source = source / "search"
    if not source.is_dir():
        parser.error(f"checkpoint directory not found: {source}")
    target = args.root.resolve() / "search"
    target.mkdir(exist_ok=True)
    copied = 0
    identical = 0
    for src in sorted(source.glob("*.jsonl")):
        data = src.read_bytes()
        dst = target / src.name
        if dst.exists():
            if dst.read_bytes() == data:
                identical += 1
                continue
            tag = hashlib.sha256(data).hexdigest()[:10]
            dst = target / f"imported_{tag}_{src.name}"
            if dst.exists() and dst.read_bytes() == data:
                identical += 1
                continue
        shutil.copy2(src, dst)
        copied += 1
        print(f"[import] {src.name} -> {dst.name}")
    print(f"[import] copied={copied} identical={identical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
