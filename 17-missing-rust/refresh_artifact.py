#!/usr/bin/env python3
"""Embed the newest reproducible receipts directly in Artifact 17's main note.

The artifact remains readable as one Markdown file after export. Timestamped raw
reports and the CSV time series are still retained under ``reports/``.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "17-missing-rust.md"
REPORTS = ROOT / "reports"
BEGIN = "<!-- BEGIN GENERATED LATEST RECEIPTS -->"
END = "<!-- END GENERATED LATEST RECEIPTS -->"


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return "_No report has been recorded yet._"


def demote_headings(text: str, levels: int = 2) -> str:
    """Keep embedded report headings below the surrounding artifact heading."""
    rendered: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            marks, sep, rest = line.partition(" ")
            if sep and set(marks) == {"#"}:
                line = "#" * min(6, len(marks) + levels) + " " + rest
        rendered.append(line)
    return "\n".join(rendered)


def main() -> int:
    original = MAIN.read_text(encoding="utf-8", errors="replace")
    if BEGIN in original and END in original:
        before = original.split(BEGIN, 1)[0].rstrip()
        after = original.split(END, 1)[1].lstrip()
        original = before + ("\n\n" + after if after else "\n")

    probe = demote_headings(read(REPORTS / "latest_probe.md"))
    watch = demote_headings(read(REPORTS / "latest_resource_watch.md"))
    block = f"""{BEGIN}
## Latest generated run receipts

This block is updated automatically whenever the capability probe or resource
watch runs. It keeps the most recent printable evidence in this main artifact
file. Timestamped originals and the raw resource CSV remain in `reports/`.

### Latest language capability probe

{probe}

### Latest resource watch

{watch}

{END}
"""
    MAIN.write_text(original.rstrip() + "\n\n" + block, encoding="utf-8")
    print(MAIN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
