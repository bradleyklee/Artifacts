#!/usr/bin/env python3
"""Atomically compact one just-sealed legacy block into the V3 archival format."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from compact_blocks import compact_one


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("block", type=Path, help="legacy .block.tar.gz produced by seal_block.py")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Artifact 18 source root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    source = args.block.resolve()
    if not source.is_file():
        raise SystemExit(f"missing block: {source}")
    staged = source.with_name(f".{source.name}.compact")
    staged.unlink(missing_ok=True)
    old_bytes, compact_bytes = compact_one(source, staged, repo)
    os.replace(staged, source)
    print(json.dumps({
        "block": str(source),
        "source_bytes": old_bytes,
        "compact_bytes": compact_bytes,
        "schema": "exact-two-body-compact-block/v3",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
