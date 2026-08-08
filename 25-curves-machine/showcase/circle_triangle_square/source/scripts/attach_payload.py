#!/usr/bin/env python3
"""Attach the autonomous-referee payload to the compiled PDF."""
from __future__ import annotations

import argparse
from pathlib import Path
import fitz

ATTACHMENTS = [
    "MANIFEST.sha256",
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
    "verify_certificate.py",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--payload-dir", type=Path, default=Path("payload"))
    args = parser.parse_args()

    missing = [name for name in ATTACHMENTS if not (args.payload_dir / name).is_file()]
    if missing:
        raise SystemExit(f"missing payload files: {', '.join(missing)}")

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.input_pdf)
    for name in ATTACHMENTS:
        path = args.payload_dir / name
        doc.embfile_add(
            name,
            path.read_bytes(),
            filename=name,
            ufilename=name,
            desc="Circle Triangle Square autonomous referee payload",
        )
    doc.save(args.output_pdf, garbage=4, deflate=True, clean=True)
    doc.close()


if __name__ == "__main__":
    main()
