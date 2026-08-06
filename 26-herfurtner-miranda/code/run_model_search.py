#!/usr/bin/env python3
"""Print the known catalog and run bounded exact curve-model searches."""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import textwrap
from collections import defaultdict
from pathlib import Path
from time import perf_counter

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PLANE_DIR = ROOT / "code" / "plane_scan"
sys.path.insert(0, str(PLANE_DIR))

from plane_scan import cubic, quartic  # noqa: E402
from plane_scan.classify import canonical_fibers  # noqa: E402

DATA = ROOT / "examples" / "data"
KNOWN_FILE = DATA / "models_11_release.json"
TARGET_FILE = DATA / "four_fibre_allowable_v2.json"
OUTPUT_FILE = DATA / "model_search_results.json"
PUBLIC_CATALOGUE = ROOT / "examples" / "public" / "catalogue"
CATALOGUE_TEXT = PUBLIC_CATALOGUE / "CURVES.txt"
CATALOGUE_JSON = PUBLIC_CATALOGUE / "curves.json"
COMPLETE_FILE = ROOT / "examples" / "public" / "complete_cases.json"


def progress(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def fiber_code(fibers: tuple[str, ...]) -> str:
    return " ".join(fibers)


def invariant_key(result: dict[str, object]) -> tuple[str, str, str]:
    return (
        str(result["c4"]),
        str(result["c6"]),
        str(result["delta"]),
    )


def exact_terms(expression: str) -> list[dict[str, object]]:
    p_symbol, q_symbol = sp.symbols("p q")
    value = sp.sympify(expression, locals={"p": p_symbol, "q": q_symbol})
    polynomial = sp.Poly(value, p_symbol, q_symbol)
    return [
        {
            "p_power": powers[0],
            "q_power": powers[1],
            "coefficient": sp.sstr(coefficient),
        }
        for powers, coefficient in polynomial.terms()
    ]


def load_known_catalog() -> list[dict[str, object]]:
    source = json.loads(KNOWN_FILE.read_text())
    complete_source = json.loads(COMPLETE_FILE.read_text())
    complete = {item["model"]: item for item in complete_source["models"]}
    family_names = {
        "harmonic_plus_cubic": "harmonic cubic",
        "two_node_structured_quartic": "structured quartic",
    }
    rows = []
    for item in source["models"]:
        fibers = canonical_fibers(item["fibres"])
        index = item["index"]
        status = "complete" if index in complete else "incomplete"
        oeis_id = complete.get(index, {}).get("oeis_id")
        rows.append({
            "code": fiber_code(fibers),
            "fiber_classification": list(fibers),
            "model_number": index,
            "presentation_number": 1,
            "plane_model_type": family_names.get(
                item["family"], item["family"]
            ),
            "family_key": item["family"],
            "hamiltonian_2H": item["hamiltonian_2H"],
            "hamiltonian_terms": exact_terms(item["hamiltonian_2H"]),
            "arithmetic_scale": item["observed_small_scale_M"],
            "period_status": "exact",
            "laurent_status": status,
            "status": status,
            "oeis_id": oeis_id,
        })
    return sorted(
        rows,
        key=lambda row: (
            row["code"],
            row["model_number"],
            row["presentation_number"],
        ),
    )


def load_targets() -> set[tuple[str, ...]]:
    source = json.loads(TARGET_FILE.read_text())
    return {
        canonical_fibers(item["fibers"])
        for item in source["configurations"]
        if item["j_degree"] > 0
    }


def search_cubics(
    bound: int,
    allowed: set[tuple[str, ...]],
    progress_every: int,
) -> list[dict[str, object]]:
    values = range(-bound, bound + 1)
    total = (2 * bound + 1) ** 4 - 1
    found = []
    started = perf_counter()
    checked = 0
    progress(f"[model-search] cubic pass: {total} coefficient tuples")
    for values4 in itertools.product(values, repeat=4):
        if values4 == (0, 0, 0, 0):
            continue
        checked += 1
        try:
            parameters = cubic.CubicParameters.from_values(*values4)
            result = cubic.verify(parameters)
        except (
            ValueError,
            sp.PolynomialError,
            ZeroDivisionError,
        ):
            result = None
        if result is not None:
            fibers = canonical_fibers(result["fibers"])
            if result["euler_total"] == 12 and fibers in allowed:
                found.append({
                    "family": "harmonic_plus_cubic",
                    "fibers": list(fibers),
                    "parameters": result["parameters"],
                    "hamiltonian_2H": result["hamiltonian_2H"],
                    "c4": result["c4"],
                    "c6": result["c6"],
                    "delta": result["delta"],
                })
        if checked % progress_every == 0 or checked == total:
            elapsed = perf_counter() - started
            progress(
                f"[model-search] cubic {checked}/{total}; "
                f"hits {len(found)}; {elapsed:.1f}s"
            )
    return found


def verify_known_quartics(
    allowed: set[tuple[str, ...]],
) -> list[dict[str, object]]:
    found = []
    total = len(quartic.WITNESSES)
    progress(f"[model-search] quartic witnesses: {total}")
    for checked, parameters in enumerate(
        quartic.WITNESSES.values(),
        start=1,
    ):
        result = quartic.verify(parameters)
        fibers = canonical_fibers(result["fibers"])
        if result["euler_total"] != 12 or fibers not in allowed:
            raise AssertionError("stored quartic witness failed")
        found.append({
            "family": "two_node_structured_quartic",
            "fibers": list(fibers),
            "parameters": result["parameters"],
            "hamiltonian_2H": result["hamiltonian_2H"],
            "c4": result["c4"],
            "c6": result["c6"],
            "delta": result["delta"],
        })
        progress(
            f"[model-search] quartic witness {checked}/{total}: "
            f"{fiber_code(fibers)}"
        )
    return found


def summarize_hits(
    hits: list[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[
        tuple[str, ...],
        list[dict[str, object]],
    ] = defaultdict(list)
    for hit in hits:
        grouped[tuple(hit["fibers"])].append(hit)
    rows = []
    for fibers in sorted(grouped, key=fiber_code):
        items = grouped[fibers]
        unique = {}
        for item in items:
            unique[invariant_key(item)] = item
        rows.append({
            "code": fiber_code(fibers),
            "fibers": list(fibers),
            "presentations": len(items),
            "invariant_models": len(unique),
            "families": sorted({
                str(item["family"])
                for item in items
            }),
            "representatives": list(unique.values()),
        })
    return rows


def catalogue_text(
    rows: list[dict[str, object]],
    verbose: bool = False,
) -> str:
    lines = [
        f"Retained curve catalogue ({len(rows)})",
        "",
        "MODEL  FIBERS                SCALE     STATUS      HAMILTONIAN",
        "-----  --------------------  --------  ----------  ----------------",
    ]
    for row in rows:
        prefix = (
            f"{row['model_number']:<5}  "
            f"{row['code']:<20}  "
            f"{str(row['arithmetic_scale']):>8}  "
            f"{row['status']:<10}  "
        )
        equation = f"2H = {row['hamiltonian_2H']}"
        wrapped = textwrap.wrap(
            equation,
            width=max(20, 80-len(prefix)),
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        lines.append(prefix + wrapped[0])
        continuation = " " * len(prefix)
        lines.extend(continuation + part for part in wrapped[1:])
        if verbose:
            details = (
                f"type={row['plane_model_type']}; "
                f"period={row['period_status']}; "
                f"Laurent={row['laurent_status']}; "
                f"OEIS={row['oeis_id'] or '-'}"
            )
            detail_lines = textwrap.wrap(
                details,
                width=72,
                initial_indent="        ",
                subsequent_indent="        ",
                break_long_words=False,
                break_on_hyphens=False,
            )
            lines.extend(detail_lines)
    return "\n".join(lines) + "\n"


def write_catalogue(rows: list[dict[str, object]]) -> None:
    PUBLIC_CATALOGUE.mkdir(parents=True, exist_ok=True)
    CATALOGUE_TEXT.write_text(catalogue_text(rows), encoding="utf-8")
    payload = {
        "schema_version": 1,
        "sort_order": [
            "fiber classification",
            "model number",
            "presentation number",
        ],
        "curves": rows,
    }
    CATALOGUE_JSON.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def print_catalogue(
    rows: list[dict[str, object]],
    verbose: bool = False,
) -> None:
    print(catalogue_text(rows, verbose=verbose), end="")


def print_search(rows: list[dict[str, object]]) -> None:
    print()
    print(f"Search results ({len(rows)} Kodaira codes)")
    print("Kodaira code                     Hits  Models  Families")
    print("-------------------------------  ----  ------  --------------------")
    for row in rows:
        families = ",".join(row["families"])
        print(
            f"{row['code']:<31}  {row['presentations']:>4}  "
            f"{row['invariant_models']:>6}  {families}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print the 11 known exact curve models, then search a "
            "bounded integral cubic box and verify known quartics."
        )
    )
    parser.add_argument(
        "--known-only",
        action="store_true",
        help="backward-compatible alias for --print-catalogue",
    )
    parser.add_argument(
        "--print-catalogue",
        action="store_true",
        help="print the retained curve catalogue without searching",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="include period, Laurent, model-type, and OEIS metadata",
    )
    parser.add_argument(
        "--cubic-bound",
        type=int,
        default=3,
        help="search cubic coefficients from -B through B (default: 3)",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=250,
        help="report progress every N cubic candidates (default: 250)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="JSON output path (default: model_search_results.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cubic_bound < 0:
        raise SystemExit("--cubic-bound must be nonnegative")
    if args.progress_every < 1:
        raise SystemExit("--progress-every must be positive")

    known = load_known_catalog()
    write_catalogue(known)
    if args.known_only or args.print_catalogue:
        print_catalogue(known, verbose=args.verbose)
        return

    allowed = load_targets()
    hits = search_cubics(
        args.cubic_bound,
        allowed,
        args.progress_every,
    )
    hits.extend(verify_known_quartics(allowed))
    rows = summarize_hits(hits)
    known_codes = {row["code"] for row in known}
    found_codes = {row["code"] for row in rows}
    new_codes = sorted(found_codes - known_codes)
    result = {
        "scope": {
            "cubic_coefficients": [
                -args.cubic_bound,
                args.cubic_bound,
            ],
            "cubic_tuples": (2 * args.cubic_bound + 1) ** 4 - 1,
            "quartic_witnesses_rechecked": len(quartic.WITNESSES),
            "allowable_nonconstant_j_targets": len(allowed),
        },
        "known_catalog": known,
        "summary": {
            "raw_presentations": len(hits),
            "kodaira_codes_found": len(rows),
            "invariant_models_found": sum(
                row["invariant_models"] for row in rows
            ),
            "new_kodaira_codes": new_codes,
        },
        "results_by_kodaira_code": rows,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print_search(rows)
    print()
    print(
        "Summary: "
        f"{len(hits)} presentations; "
        f"{result['summary']['invariant_models_found']} models; "
        f"{len(rows)} Kodaira codes; "
        f"{len(new_codes)} new codes."
    )
    try:
        display_output = args.output.resolve().relative_to(ROOT.resolve())
    except ValueError:
        display_output = args.output
    print(f"JSON: {display_output}")
    print()
    print_catalogue(known, verbose=args.verbose)
    print("Catalogue JSON: examples/public/catalogue/curves.json")


if __name__ == "__main__":
    main()
