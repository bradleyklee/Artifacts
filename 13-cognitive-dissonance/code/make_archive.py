#!/usr/bin/env python3
"""Create a self-contained ZIP archive without recursively including dist/."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SKIP_DIRS = {"dist", "__pycache__", ".git"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    prefix = root.name
    with ZipFile(out, "w", ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root)
            if any(part in SKIP_DIRS for part in rel.parts) or not path.is_file() or path.resolve() == out:
                continue
            zf.write(path, Path(prefix) / rel)
    print(out)


if __name__ == "__main__":
    main()
