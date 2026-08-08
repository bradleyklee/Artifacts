#!/usr/bin/env python3
"""Build, verify, and attach the autonomous-referee payload."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "release"
BASENAME = "circle_triangle_square_periods_certificate_v19_source_standardized_payload.pdf"


def run(command: list[str], *, cwd: Path = ROOT, stdout=None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True, stdout=stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate-figure", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args()

    if args.regenerate_figure:
        run([sys.executable, "scripts/generate_quantized_levels.py"])
        run([sys.executable, "scripts/generate_figure.py"])

    shutil.copy2(ROOT / "certificate_source.tex", ROOT / "payload/certificate_source.tex")
    shutil.copy2(ROOT / "scripts/generate_figure.py", ROOT / "payload/generate_figure.py")
    shutil.copy2(ROOT / "scripts/generate_quantized_levels.py", ROOT / "payload/generate_quantized_levels.py")
    shutil.copy2(ROOT / "CERTIFICATE_SOURCE_BUNDLE_STANDARD.md", ROOT / "payload/SOURCE_BUNDLE_STANDARD.md")

    if not args.skip_verify:
        with (ROOT / "payload/verification_output.txt").open("w", encoding="utf-8") as output:
            run([sys.executable, "verify_certificate.py"], cwd=ROOT / "payload", stdout=output)
        print((ROOT / "payload/verification_output.txt").read_text(encoding="utf-8"), end="")

    run([sys.executable, "scripts/update_manifest.py", "--payload-only"])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "certificate_source.tex"])

    RELEASE.mkdir(exist_ok=True)
    output_pdf = RELEASE / BASENAME
    if output_pdf.exists():
        output_pdf.unlink()
    run([
        sys.executable,
        "scripts/attach_payload.py",
        "certificate_source.pdf",
        str(output_pdf),
        "--payload-dir",
        "payload",
    ])
    run([sys.executable, "scripts/update_manifest.py", "--project-only"])
    print(f"built {output_pdf.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
