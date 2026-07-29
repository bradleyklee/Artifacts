#!/usr/bin/env python3
"""Generate the transparent four-family mapped-area period cache.

The red coefficients come from ``compute_mesh_area_series.py``.  The three
Abel-Wick coefficients come from ``abel_wick_period_series.py``.  The output is
an ordinary CSV; the notebook recomputes a short exact prefix before trusting
this longer cache.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import sympy as sp

from compute_mesh_area_series import compute as compute_red_area
from abel_wick_period_series import (
    FAMILY_NAMES,
    SCALES as ABEL_WICK_SCALES,
    period_coefficients as compute_abel_wick_period,
)

RED_SCALE = sp.Integer(235_651_734)


def red_period_coefficients(terms: int) -> list[sp.Expr]:
    area = compute_red_area(terms)["coeffs"]
    return [sp.factor((k + 1) * area[k + 1]) for k in range(terms)]


def rows_for_family(name: str, coefficients: list[sp.Expr], scale: sp.Integer):
    for k, coefficient in enumerate(coefficients):
        scaled = sp.cancel(coefficient * scale**k)
        yield {
            "family": name,
            "k": k,
            "period_coefficient": str(coefficient),
            "scale": str(scale),
            "scaled_integer": str(scaled),
            "is_integer": str(sp.denom(scaled) == 1).lower(),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--red-terms", type=int, default=20)
    parser.add_argument("--abel-wick-terms", type=int, default=20)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "mapped_area_period_scaled_integers.csv",
    )
    args = parser.parse_args()

    rows = list(rows_for_family("red", red_period_coefficients(args.red_terms), RED_SCALE))
    for family in FAMILY_NAMES:
        coefficients, _ = compute_abel_wick_period(
            family, args.abel_wick_terms, progress=args.progress
        )
        rows.extend(rows_for_family(family, coefficients, ABEL_WICK_SCALES[family]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if row["is_integer"] != "true"]
    if failures:
        raise AssertionError(f"first noninteger row: {failures[0]}")
    print(args.out)
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
