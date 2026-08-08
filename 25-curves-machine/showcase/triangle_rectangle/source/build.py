#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "release"
PAYLOAD = ROOT / "payload"
ANALYSIS = ROOT / "analysis"
BASENAME = "triangle_rectangle_genus_one_periods_certificate_v5_17_payload.pdf"


def run(cmd: list[str], cwd: Path = ROOT, stdout=None) -> None:
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=cwd, check=True, stdout=stdout)


def copy_payload_sources() -> None:
    session_dir = PAYLOAD / "session_code"
    if session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ROOT / "certificate_source.tex", PAYLOAD / "certificate_source.tex")
    shutil.copy2(ROOT / "verify_certificate.py", PAYLOAD / "verify_certificate.py")
    shutil.copy2(ROOT / "verify_continued_eisenstein_root.py", PAYLOAD / "verify_continued_eisenstein_root.py")
    shutil.copy2(ROOT / "scripts/generate_figure.py", PAYLOAD / "generate_figure.py")
    shutil.copy2(ROOT / "scripts/generate_quantized_levels.py", PAYLOAD / "generate_quantized_levels.py")
    shutil.copy2(ROOT / "CERTIFICATE_SOURCE_BUNDLE_STANDARD.md", PAYLOAD / "SOURCE_BUNDLE_STANDARD.md")

    for source in (
        ROOT / "scripts/verify_hypergeometric_transform_chain.py",
        ANALYSIS / "hypergeometric_transform_chain.json",
        ROOT / "docs/SOURCES.md",
    ):
        shutil.copy2(source, session_dir / source.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate-figure", action="store_true")
    parser.add_argument("--regenerate-analysis", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args()

    if args.regenerate_analysis:
        run([sys.executable, "scripts/verify_hypergeometric_transform_chain.py"])

    if args.regenerate_figure:
        run([sys.executable, "scripts/generate_quantized_levels.py"])
        run([sys.executable, "scripts/generate_figure.py"])

    copy_payload_sources()

    if not args.skip_verify:
        with (PAYLOAD / "verification_output.txt").open("w", encoding="utf-8") as out:
            run([sys.executable, "verify_certificate.py"], cwd=PAYLOAD, stdout=out)
        print((PAYLOAD / "verification_output.txt").read_text(encoding="utf-8"), end="")

    run([sys.executable, "scripts/update_manifest.py", "--payload-only"])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "certificate_source.tex"])

    RELEASE.mkdir(exist_ok=True)
    output = RELEASE / BASENAME
    if output.exists():
        output.unlink()
    run([
        sys.executable,
        "scripts/attach_payload.py",
        "certificate_source.pdf",
        str(output),
        "--payload-dir",
        "payload",
    ])
    run([sys.executable, "scripts/update_manifest.py", "--project-only"])
    print("built", output.relative_to(ROOT))


if __name__ == "__main__":
    main()
