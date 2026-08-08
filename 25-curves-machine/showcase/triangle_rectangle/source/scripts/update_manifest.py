#!/usr/bin/env python3
"""Update recursive SHA-256 manifests for the embedded payload and project."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payload"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_payload_manifest() -> None:
    # The PDF embeds this compact autonomous-review set. Extended session
    # derivations remain covered by PROJECT_MANIFEST.sha256 in the full ZIP.
    embedded = [
        "README_AUTONOMOUS_REVIEW.txt",
        "certificate_payload.json",
        "certificate_source.tex",
        "claim_index.json",
        "generate_figure.py",
        "generate_quantized_levels.py",
        "quantization_spec.json",
        "SOURCE_BUNDLE_STANDARD.md",
        "quantized_levels_for_figure.csv",
        "verification_output.txt",
        "verification_results.json",
        "continued_eisenstein_root_check.json",
        "continued_eisenstein_root_check.csv",
        "solution_basis_audit.json",
        "solution_basis_audit.csv",
        "verify_certificate.py",
        "verify_continued_eisenstein_root.py",
    ]
    files = [PAYLOAD / name for name in embedded]
    missing = [path.name for path in files if not path.is_file()]
    if missing:
        raise SystemExit("missing embedded payload files: " + ", ".join(missing))
    lines = [f"{digest(path)}  {path.name}" for path in files]
    (PAYLOAD / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote payload/MANIFEST.sha256")


def write_project_manifest() -> None:
    excluded_names = {
        "PROJECT_MANIFEST.sha256",
        "certificate_source.aux",
        "certificate_source.log",
        "certificate_source.out",
        "certificate_source.pdf",
    }
    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and path.name not in excluded_names
    )
    lines = [f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in files]
    (ROOT / "PROJECT_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote PROJECT_MANIFEST.sha256")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--payload-only", action="store_true")
    group.add_argument("--project-only", action="store_true")
    args = parser.parse_args()

    if args.project_only:
        write_project_manifest()
    elif args.payload_only:
        write_payload_manifest()
    else:
        write_payload_manifest()
        write_project_manifest()


if __name__ == "__main__":
    main()
