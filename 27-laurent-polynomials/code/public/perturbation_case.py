#!/usr/bin/env python3
"""Run one perturbation in a fresh process and print one exact JSON record."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "code" / "guvj"))

from all_orders_solver import SearchExhausted, derive, parse_laurent  # noqa: E402


def json_ready(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--F", required=True)
    parser.add_argument("--max-order", type=int)
    parser.add_argument("--max-support-level", type=int)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    F = parse_laurent(args.F)
    record: dict[str, Any] = {"F": str(F)}
    try:
        result = derive(
            F,
            max_order=args.max_order,
            max_support_level=args.max_support_level,
            progress_enabled=not args.quiet,
        )
        record.update({
            "status": "certificate_found",
            "operator": str(result["operator"]),
            "recurrence": json_ready(result["recurrence"]),
            "operator_stats": result["operator_stats"],
            "certificate": {
                "support_family": result["certificate"]["support_family"],
                "support_level": result["certificate"]["support_level"],
                "layer_basis_sizes": result["certificate"][
                    "layer_basis_sizes"
                ],
                "matrix_shape": result["certificate"]["matrix_shape"],
            },
            "checks": result["checks"],
        })
    except SearchExhausted as error:
        record.update({
            "status": "resource_controls_exhausted",
            "message": str(error),
        })
    record["elapsed_seconds"] = round(time.perf_counter() - started, 6)
    print(json.dumps(json_ready(record), sort_keys=True))


if __name__ == "__main__":
    main()
