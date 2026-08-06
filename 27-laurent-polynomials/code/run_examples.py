#!/usr/bin/env python3
"""Run public examples, private examples, or both without crossing data roots."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PROJECT_ROOT / "code"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def replay_public() -> None:
    """Verify only records stored under examples/public/."""
    run([sys.executable, str(CODE_ROOT / "public" / "verify_catalogue.py")])


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
        help="re-solve the selected G,U,V,J records after replaying them",
    )
    args = parser.parse_args()

    if args.scope in {"public", "all"}:
        replay_public()
    if args.scope in {"private", "all"}:
        if args.data_root is None:
            parser.error("--data-root is required for private or all scope")
        replay_private(args.data_root)
        if args.derive_guvj:
            derive_private_guvj(args.data_root)
    elif args.derive_guvj:
        parser.error("--derive-guvj applies only when a G,U,V,J data root is selected")


if __name__ == "__main__":
    main()
