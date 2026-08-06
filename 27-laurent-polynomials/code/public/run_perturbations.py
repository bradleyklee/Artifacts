#!/usr/bin/env python3
"""Systematically perturb a Laurent model and checkpoint exact certificates."""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "code" / "guvj"))

from example import model_by_id  # noqa: E402
from all_orders_solver import laurent_terms, parse_laurent, x, y  # noqa: E402

WORKER = Path(__file__).with_name("perturbation_case.py")


def shell(radius: int):
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if max(abs(i), abs(j)) == radius:
                yield i, j


def available_monomials(base: sp.Expr, radius: int):
    occupied = set(laurent_terms(base))
    for current_radius in range(1, radius + 1):
        for i, j in shell(current_radius):
            if (i, j) not in occupied:
                yield current_radius, i, j


def perturbations(
    base: sp.Expr,
    radius: int,
    coefficients: list[int],
    max_added_terms: int,
    pair_limit: int | None,
):
    monomials = list(available_monomials(base, radius))
    for current_radius, i, j in monomials:
        monomial = x ** i * y ** j
        for coefficient in coefficients:
            yield {
                "kind": "single",
                "radius": current_radius,
                "exponents": [[i, j]],
                "coefficients": [coefficient],
                "F": sp.expand(base + coefficient * monomial),
            }

    if max_added_terms < 2:
        return
    produced = 0
    for left, right in itertools.combinations(monomials, 2):
        radius_left, i, j = left
        radius_right, r, s = right
        for coefficient_left in coefficients:
            for coefficient_right in coefficients:
                yield {
                    "kind": "pair",
                    "radius": max(radius_left, radius_right),
                    "exponents": [[i, j], [r, s]],
                    "coefficients": [coefficient_left, coefficient_right],
                    "F": sp.expand(
                        base
                        + coefficient_left * x ** i * y ** j
                        + coefficient_right * x ** r * y ** s
                    ),
                }
                produced += 1
                if pair_limit is not None and produced >= pair_limit:
                    return


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_case(item: dict, args: argparse.Namespace) -> dict:
    command = [sys.executable, str(WORKER), "--F", str(item["F"])]
    if args.max_order is not None:
        command.extend(["--max-order", str(args.max_order)])
    if args.max_support_level is not None:
        command.extend([
            "--max-support-level", str(args.max_support_level)
        ])
    if args.quiet:
        command.append("--quiet")
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE if args.quiet else None,
            check=True,
            timeout=args.case_timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "resource_timeout",
            "message": (
                "per-case resource control expired; this is not a "
                "mathematical failure"
            ),
        }
    return json.loads(completed.stdout.strip().splitlines()[-1])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="regression:triangle")
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--coefficients", default="1,-1,2,-2")
    parser.add_argument("--max-added-terms", type=int, choices=(1, 2), default=2)
    parser.add_argument("--pair-limit", type=int, default=24)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-order", type=int)
    parser.add_argument("--max-support-level", type=int)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--case-timeout",
        type=float,
        default=None,
        help="optional resource control; omitted means no timeout",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "examples" / "public" /
        "PERTURBATIONS_CERTIFIED.json",
    )
    args = parser.parse_args()

    base_record = model_by_id(args.base)
    base = parse_laurent(base_record["F"])
    coefficients = [int(value) for value in args.coefficients.split(",")]
    records = []
    started = time.perf_counter()
    iterator = perturbations(
        base,
        args.radius,
        coefficients,
        args.max_added_terms,
        args.pair_limit,
    )
    for index, item in enumerate(iterator, 1):
        if args.limit is not None and index > args.limit:
            break
        record = run_case(item, args)
        record.update({
            "index": index,
            "kind": item["kind"],
            "radius": item["radius"],
            "exponents": item["exponents"],
            "coefficients": item["coefficients"],
            "F": str(item["F"]),
        })
        records.append(record)
        save(args.output, {
            "schema": "laurent-period-certified-perturbations-v2",
            "base": args.base,
            "base_F": str(base),
            "controls": {
                "radius": args.radius,
                "coefficients": coefficients,
                "max_added_terms": args.max_added_terms,
                "pair_limit": args.pair_limit,
                "max_order": args.max_order,
                "max_support_level": args.max_support_level,
                "case_timeout": args.case_timeout,
            },
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "records": records,
        })
        order = record.get("operator_stats", {}).get("order", "-")
        print(
            f"[{index}] kind={item['kind']} exponents={item['exponents']} "
            f"status={record['status']} order={order}",
            flush=True,
        )


if __name__ == "__main__":
    main()
