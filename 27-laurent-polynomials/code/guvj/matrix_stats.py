#!/usr/bin/env python3
"""Summarize stored sparse G,U,V,J records under an explicit data root.

The report is written below the selected data root, so public and private
statistics cannot cross storage boundaries accidentally.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_info(record: dict[str, Any]) -> tuple[str, int, float]:
    rows, columns = record["shape"]
    nonzero = int(record["nonzero_count"])
    total = int(rows) * int(columns)
    density = 100.0 * nonzero / total if total else 0.0
    return f"{rows} x {columns}", nonzero, density


def format_cell(record: dict[str, Any]) -> str:
    shape, nonzero, density = matrix_info(record)
    return f"{shape}; {nonzero} nnz ({density:.1f}%)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root.is_absolute():
        data_root = PROJECT_ROOT / data_root
    reference_root = data_root / "reference"
    records = [read_json(path) for path in sorted(reference_root.glob("*.json"))]
    if not records:
        raise FileNotFoundError(f"no reference JSON files found under {reference_root}")

    lines = [
        "# Stored G,U,V,J matrix statistics",
        "",
        "Generated from the exact sparse records under `reference/` by:",
        "",
        "```text",
        f"python code/guvj/matrix_stats.py --data-root {data_root.relative_to(PROJECT_ROOT)}",
        "```",
        "",
        "Here `d = |B|` and `m = |C|`.  The stored selected-column form has",
        "`G` of size `m x 3d`, `J` of size `d x 2d`, and `U`, `Vx`, `Vy`",
        "of size `d x 1`.  `nnz` means the number of nonzero sparse entries.",
        "",
        "| Record | d | m | G | J | U | Vx | Vy |",
        "|---|---:|---:|---|---|---|---|---|",
    ]

    for record in records:
        basis = record["basis"]
        matrices = record["matrices"]
        reduction = record["reduction"]
        lines.append(
            "| {model} | {d} | {m} | {G} | {J} | {U} | {Vx} | {Vy} |".format(
                model=record["model"],
                d=len(basis["B"]),
                m=len(basis["C"]),
                G=format_cell(matrices["G"]),
                J=format_cell(matrices["J"]),
                U=format_cell(reduction["U"]),
                Vx=format_cell(reduction["Vx"]),
                Vy=format_cell(reduction["Vy"]),
            )
        )

    lines.extend([
        "",
        "Every stored record also contains the two reduced columns, the `2 x 3`",
        "kernel matrix used to obtain the order-two operator, twelve constant",
        "terms, and five independent direct-power checks.",
        "",
    ])

    output = args.output or (data_root / "MATRIX_STATS.md")
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
