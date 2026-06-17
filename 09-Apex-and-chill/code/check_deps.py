#!/usr/bin/env python3
"""Dependency check for the minimal release package."""
from __future__ import annotations
import importlib.util
import sys

REQUIRED = [
    ("json", "stdlib", "JSON parsing"),
    ("xml.etree.ElementTree", "stdlib", "SVG vector extraction"),
]


def main() -> int:
    missing = []
    for module, package, needed in REQUIRED:
        if importlib.util.find_spec(module) is None:
            missing.append((module, package, needed))
    if missing:
        print("[FAIL] missing runtime dependency")
        for module, package, needed in missing:
            print(f"  module: {module}")
            print(f"  package: {package}")
            print(f"  needed: {needed}")
        return 2
    print("[OK] dependency check: stdlib only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
