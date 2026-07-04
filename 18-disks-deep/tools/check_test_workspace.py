#!/usr/bin/env python3
"""Validate the disposable two-division workspace created by `make test`."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args()
    tool = Path(__file__).resolve().parent / "check_corpus.py"
    return subprocess.run([
        sys.executable, str(tool), "--root", str(args.root), "--target", str(args.target), "--full"
    ]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
