#!/usr/bin/env python3
"""Run public examples, private examples, or both without crossing data roots."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PROJECT_ROOT / "code"


def displayed_argument(argument: str) -> str:
    """Use short project-relative paths in echoed commands."""
    if Path(argument) == Path(sys.executable):
        return "python3"
    try:
        return str(Path(argument).resolve().relative_to(PROJECT_ROOT))
    except (OSError, ValueError):
        return argument


def run(command: list[str]) -> None:
    shown = shlex.join([displayed_argument(argument) for argument in command])
    for line in textwrap.wrap(
        "+ " + shown,
        width=80,
        subsequent_indent="  ",
        break_long_words=True,
        break_on_hyphens=False,
    ) or ["+"]:
        print(line, flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def replay_public() -> None:
    """Verify only records stored under examples/public/."""
    run([sys.executable, str(CODE_ROOT / "public" / "verify_catalogue.py")])


def derive_public_guvj() -> None:
    """Recompute every distinct canonical public Laurent model."""
    output_root = PROJECT_ROOT / "results" / "public" / "canonical"
    output_root.mkdir(parents=True, exist_ok=True)
    models = (
        ("A295870", "A295870.json"),
        ("public:1", "catalogue-model-1.json"),
        ("A303790", "A303790.json"),
        ("public:3", "catalogue-model-3.json"),
        ("public:9", "catalogue-model-9.json"),
    )
    for model, filename in models:
        command = [sys.executable, str(CODE_ROOT / "example.py")]
        if model.startswith("public:"):
            command.extend(["derive", "--model", model])
        else:
            command.extend(["certify", model])
        command.extend(["--output", str(output_root / filename)])
        run(command)


def replay_private(data_root: Path) -> None:
    """Verify a G,U,V,J dataset under the explicitly selected data root."""
    run([
        sys.executable,
        str(CODE_ROOT / "guvj" / "replay_dataset.py"),
        "--data-root", str(data_root),
        "--report", str(data_root / "REPLAY_REPORT.json"),
    ])


def derive_private_guvj(data_root: Path) -> None:
    run([
        sys.executable,
        str(CODE_ROOT / "guvj" / "verify_all.py"),
        "--models", str(data_root / "models.json"),
        "--output-dir", str(data_root / "reference"),
        "--report", str(data_root / "VERIFICATION_REPORT.json"),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", choices=("public", "private", "all"))
    parser.add_argument(
        "--data-root", type=Path,
        help="G,U,V,J dataset root; required for private or all scope",
    )
    parser.add_argument(
        "--derive-guvj",
        action="store_true",
        help="re-solve canonical G,U,V,J records after replay",
    )
    args = parser.parse_args()

    if args.scope in {"public", "all"}:
        replay_public()
        if args.derive_guvj:
            derive_public_guvj()
    if args.scope in {"private", "all"}:
        if args.data_root is None:
            parser.error("--data-root is required for private or all scope")
        replay_private(args.data_root)
        if args.derive_guvj:
            derive_private_guvj(args.data_root)


if __name__ == "__main__":
    main()
