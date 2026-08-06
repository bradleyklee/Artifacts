#!/usr/bin/env python3
"""Build the public release from an explicit allowlist and reject private paths."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = (
    Path(".gitignore"),
    Path("README.md"),
    Path("WALKTHROUGH_PUBLIC.md"),
    Path("requirements.txt"),
    Path("note.pdf"),
    Path("paper/note.tex"),
    Path("paper/note.pdf"),
    Path("pseudo"),
    Path("code/a303790"),
    Path("code/public"),
    Path("code/guvj"),
    Path("code/run_examples.py"),
    Path("code/example.py"),
    Path("code/tests"),
    Path("code/test_00_order4_joint.py"),
    Path("code/build_public_release.py"),
    Path("examples/public"),
)


GENERATED_SUFFIXES = {".aux", ".log", ".out", ".pyc"}


def is_release_file(path: Path) -> bool:
    return "__pycache__" not in path.parts and path.suffix not in GENERATED_SUFFIXES


def iter_files(path: Path):
    if path.is_file():
        if is_release_file(path):
            yield path
    elif path.is_dir():
        yield from sorted(
            item for item in path.rglob("*")
            if item.is_file() and is_release_file(item)
        )
    else:
        raise FileNotFoundError(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else Path.cwd() / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    files = []
    for relative in ALLOWLIST:
        files.extend(iter_files(PROJECT_ROOT / relative))

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(files)):
            relative = path.relative_to(PROJECT_ROOT)
            if relative.parts[:2] == ("examples", "private"):
                raise RuntimeError("private path reached public allowlist")
            archive.write(path, relative.as_posix())

    with zipfile.ZipFile(output) as archive:
        leaked = [name for name in archive.namelist() if name.startswith("examples/private/")]
        if leaked:
            raise RuntimeError(f"private files found in release: {leaked}")
    print(output)


if __name__ == "__main__":
    main()
