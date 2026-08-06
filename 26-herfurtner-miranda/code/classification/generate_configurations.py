#!/usr/bin/env python3
"""Derive Miranda/Persson singular-fibre configurations from scratch.

This is the missing front end of the Herfurtner-Miranda artifact.  It:

1. enumerates every unordered Kodaira-fibre multiset with Euler sum 12;
2. applies Miranda's numerical tests (1.3)--(1.11);
3. removes the 14 exceptional impossible configurations in Table (2.1);
4. extracts the allowable four-fibre slice and its nonconstant-J part.

The implementation is standard-library only.  ``--check`` derives all outputs
in memory and compares them with the checked-in JSON ledgers.  ``--write``
regenerates the ledgers and the human-readable report.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "examples" / "data"
PAPER_DIR = ROOT / "paper"

SOURCE = {
    "paper": (
        "R. Miranda, Persson's list of singular fibers for a rational "
        "elliptic surface, Math. Z. 205 (1990), 191-211"
    ),
    "implemented_criteria": [
        "(1.3)", "(1.4)", "(1.5)", "(1.6)",
        "(1.8)", "(1.9)", "(1.10)", "(1.11)",
    ],
    "exceptional_impossibilities": (
        "Table (2.1), entries 46, 56, 67, 68, 69, 73, 76, 79, 80, "
        "82, 86, 92, 93, 94"
    ),
}

# Ordered exactly as in the recovered configuration audit.  The order is also
# the canonical display order inside every fibre multiset.
KODAIRA_TABLE = [
    {"name": "II*",  "euler": 10, "root_rank": 8, "root_discriminant": 1, "j_value": "0",          "j_multiplicity": "2 mod 3", "genus_drop": 4, "root_lattice": "E8"},
    {"name": "I4*",  "euler": 10, "root_rank": 8, "root_discriminant": 4, "j_value": "infinity",   "j_multiplicity": "4",       "genus_drop": 5, "root_lattice": "D8"},
    {"name": "I9",   "euler": 9,  "root_rank": 8, "root_discriminant": 9, "j_value": "infinity",   "j_multiplicity": "9",       "genus_drop": 4, "root_lattice": "A8"},
    {"name": "III*", "euler": 9,  "root_rank": 7, "root_discriminant": 2, "j_value": "1",          "j_multiplicity": "1 mod 2", "genus_drop": 4, "root_lattice": "E7"},
    {"name": "I3*",  "euler": 9,  "root_rank": 7, "root_discriminant": 4, "j_value": "infinity",   "j_multiplicity": "3",       "genus_drop": 4, "root_lattice": "D7"},
    {"name": "I8",   "euler": 8,  "root_rank": 7, "root_discriminant": 8, "j_value": "infinity",   "j_multiplicity": "8",       "genus_drop": 4, "root_lattice": "A7"},
    {"name": "IV*",  "euler": 8,  "root_rank": 6, "root_discriminant": 3, "j_value": "0",          "j_multiplicity": "1 mod 3", "genus_drop": 3, "root_lattice": "E6"},
    {"name": "I2*",  "euler": 8,  "root_rank": 6, "root_discriminant": 4, "j_value": "infinity",   "j_multiplicity": "2",       "genus_drop": 4, "root_lattice": "D6"},
    {"name": "I7",   "euler": 7,  "root_rank": 6, "root_discriminant": 7, "j_value": "infinity",   "j_multiplicity": "7",       "genus_drop": 3, "root_lattice": "A6"},
    {"name": "I1*",  "euler": 7,  "root_rank": 5, "root_discriminant": 4, "j_value": "infinity",   "j_multiplicity": "1",       "genus_drop": 3, "root_lattice": "D5"},
    {"name": "I6",   "euler": 6,  "root_rank": 5, "root_discriminant": 6, "j_value": "infinity",   "j_multiplicity": "6",       "genus_drop": 3, "root_lattice": "A5"},
    {"name": "I0*",  "euler": 6,  "root_rank": 4, "root_discriminant": 4, "j_value": "any finite", "j_multiplicity": "variable", "genus_drop": 3, "root_lattice": "D4"},
    {"name": "I5",   "euler": 5,  "root_rank": 4, "root_discriminant": 5, "j_value": "infinity",   "j_multiplicity": "5",       "genus_drop": 2, "root_lattice": "A4"},
    {"name": "I4",   "euler": 4,  "root_rank": 3, "root_discriminant": 4, "j_value": "infinity",   "j_multiplicity": "4",       "genus_drop": 2, "root_lattice": "A3"},
    {"name": "IV",   "euler": 4,  "root_rank": 2, "root_discriminant": 3, "j_value": "0",          "j_multiplicity": "2 mod 3", "genus_drop": 1, "root_lattice": "A2"},
    {"name": "I3",   "euler": 3,  "root_rank": 2, "root_discriminant": 3, "j_value": "infinity",   "j_multiplicity": "3",       "genus_drop": 1, "root_lattice": "A2"},
    {"name": "III",  "euler": 3,  "root_rank": 1, "root_discriminant": 2, "j_value": "1",          "j_multiplicity": "1 mod 2", "genus_drop": 1, "root_lattice": "A1"},
    {"name": "I2",   "euler": 2,  "root_rank": 1, "root_discriminant": 2, "j_value": "infinity",   "j_multiplicity": "2",       "genus_drop": 1, "root_lattice": "A1"},
    {"name": "II",   "euler": 2,  "root_rank": 0, "root_discriminant": 1, "j_value": "0",          "j_multiplicity": "1 mod 3", "genus_drop": 0, "root_lattice": "0"},
    {"name": "I1",   "euler": 1,  "root_rank": 0, "root_discriminant": 1, "j_value": "infinity",   "j_multiplicity": "1",       "genus_drop": 0, "root_lattice": "0"},
]

EXCEPTIONAL_OBSTRUCTIONS = {
    ("I6", "I3", "II", "I1"):       {"table_number": 46, "reason": "Miranda (2.6.6)"},
    ("I0*", "I3", "I2", "I1"):      {"table_number": 56, "reason": "twist of Table (2.1) #11"},
    ("I5", "I3", "II", "II"):       {"table_number": 67, "reason": "Miranda (2.6.3)"},
    ("I5", "III", "I2", "I2"):     {"table_number": 68, "reason": "Miranda (2.5.2)"},
    ("I5", "I2", "I2", "I2", "I1"): {"table_number": 69, "reason": "Miranda (2.5.2)"},
    ("I4", "I4", "III", "I1"):     {"table_number": 73, "reason": "Miranda (2.6.4)"},
    ("I4", "IV", "I3", "I1"):      {"table_number": 76, "reason": "Miranda (2.5.1)"},
    ("I4", "I3", "I3", "II"):      {"table_number": 79, "reason": "Miranda (2.5.1)"},
    ("I4", "I3", "I3", "I1", "I1"): {"table_number": 80, "reason": "Miranda (2.5.1)"},
    ("IV", "IV", "I3", "I1"):      {"table_number": 82, "reason": "Miranda (2.6.1)"},
    ("IV", "I3", "I3", "II"):      {"table_number": 86, "reason": "Miranda (2.6.2)"},
    ("I3", "I3", "I3", "III"):     {"table_number": 92, "reason": "Miranda (2.6.5)"},
    ("I3", "I3", "I3", "II", "I1"): {"table_number": 93, "reason": "Miranda (2.11)"},
    ("I3", "I3", "I2", "I2", "I2"): {"table_number": 94, "reason": "Miranda (2.5.3)"},
}

BY_NAME = {row["name"]: row for row in KODAIRA_TABLE}
UNIBRANCH = ("II", "IV", "IV*", "II*")
J_ZERO = UNIBRANCH
J_ONE = ("III", "III*")


def enumerate_euler_multisets(total: int = 12) -> Iterator[list[str]]:
    """Yield canonical unordered Kodaira multisets having Euler sum ``total``."""
    current: list[str] = []

    def rec(remaining: int, start: int) -> Iterator[list[str]]:
        if remaining == 0:
            yield list(current)
            return
        for index in range(start, len(KODAIRA_TABLE)):
            row = KODAIRA_TABLE[index]
            if row["euler"] <= remaining:
                current.append(row["name"])
                yield from rec(remaining - row["euler"], index)
                current.pop()

    yield from rec(total, 0)


def is_square(value: int) -> bool:
    return math.isqrt(value) ** 2 == value


def test_record(passed: bool, value: object, condition: str) -> dict[str, object]:
    return {"passed": passed, "value": value, "condition": condition}


def analyze_configuration(fibers: Sequence[str]) -> dict[str, object]:
    counts = Counter(fibers)
    euler_sum = sum(BY_NAME[name]["euler"] for name in fibers)
    root_rank_sum = sum(BY_NAME[name]["root_rank"] for name in fibers)
    root_discriminant_product = math.prod(
        BY_NAME[name]["root_discriminant"] for name in fibers
    )
    genus_drop_sum = sum(BY_NAME[name]["genus_drop"] for name in fibers)

    pole_fibers = [name for name in fibers if BY_NAME[name]["j_value"] == "infinity"]
    j_degree = sum(int(BY_NAME[name]["j_multiplicity"]) for name in pole_fibers)

    unibranch_count = sum(counts[name] for name in UNIBRANCH)
    j0_count = sum(counts[name] for name in J_ZERO)
    j1_count = sum(counts[name] for name in J_ONE)

    tests: dict[str, dict[str, object]] = {}
    tests["euler_1_3"] = test_record(
        euler_sum == 12, euler_sum, "sum(e)=12"
    )
    tests["picard_rank_1_4"] = test_record(
        root_rank_sum <= 8, root_rank_sum, "sum(r)<=8"
    )
    tests["extremal_square_1_5"] = test_record(
        root_rank_sum != 8 or is_square(root_discriminant_product),
        root_discriminant_product,
        "if sum(r)=8, product(delta) is a square",
    )
    tests["genus_drop_1_6"] = test_record(
        unibranch_count == 0 or genus_drop_sum <= 4,
        {"unibranch_fibers": unibranch_count, "genus_drop_sum": genus_drop_sum},
        "if II+IV+IV*+II* >= 1, sum(gamma)<=4",
    )

    if j_degree == 0:
        tests["constant_j_1_8"] = test_record(
            not (j0_count and j1_count),
            {"J0_fibers": j0_count, "J1_fibers": j1_count},
            "if degree(J)=0, all finite fixed J-values agree",
        )
        tests["j_zero_1_9"] = test_record(
            True, None, "not applicable when degree(J)=0"
        )
        tests["j_one_1_10"] = test_record(
            True, None, "not applicable when degree(J)=0"
        )
        tests["hurwitz_1_11"] = test_record(
            True, None, "not applicable when degree(J)=0"
        )
        extra_ramification = None
    else:
        tests["constant_j_1_8"] = test_record(
            True, None, "not applicable when degree(J)>0"
        )

        zero_residual = (
            j_degree
            - counts["II"]
            - counts["IV*"]
            - 2 * counts["IV"]
            - 2 * counts["II*"]
        )
        one_residual = j_degree - counts["III"] - counts["III*"]
        tests["j_zero_1_9"] = test_record(
            zero_residual >= 0 and zero_residual % 3 == 0,
            zero_residual,
            "degree(J)-ii-iv*-2iv-2ii* is nonnegative and divisible by 3",
        )
        tests["j_one_1_10"] = test_record(
            one_residual >= 0 and one_residual % 2 == 0,
            one_residual,
            "degree(J)-iii-iii* is nonnegative and divisible by 2",
        )

        # Forced ramification of J above infinity, zero and one.  The two
        # residuals are always divisible in the Euler-sum-12 enumeration; they
        # can be negative in cases rejected by (1.9) or (1.10), but the same
        # integer Hurwitz diagnostic is retained in the audit.
        forced_at_infinity = j_degree - len(pole_fibers)
        forced_at_zero = (
            counts["IV"] + counts["II*"] + 2 * (zero_residual // 3)
        )
        forced_at_one = one_residual // 2
        extra_ramification = (
            2 * j_degree
            - 2
            - forced_at_infinity
            - forced_at_zero
            - forced_at_one
        )
        tests["hurwitz_1_11"] = test_record(
            extra_ramification >= 0,
            extra_ramification,
            "extra ramification x>=0",
        )

    failed_tests = [name for name, result in tests.items() if not result["passed"]]
    numerical_pass = not failed_tests

    obstruction_data = EXCEPTIONAL_OBSTRUCTIONS.get(tuple(fibers))
    exceptional_obstruction = None
    if obstruction_data is not None:
        exceptional_obstruction = {
            "table_number": obstruction_data["table_number"],
            "fibers": list(fibers),
            "reason": obstruction_data["reason"],
        }

    if not numerical_pass:
        status = "impossible_numerical"
    elif exceptional_obstruction is not None:
        status = "impossible_exceptional"
    else:
        status = "allowable"

    return {
        "fibers": list(fibers),
        "fiber_count": len(fibers),
        "euler_sum": euler_sum,
        "root_rank_sum": root_rank_sum,
        "root_discriminant_product": root_discriminant_product,
        "genus_drop_sum": genus_drop_sum,
        "j_degree": j_degree,
        "extra_ramification": extra_ramification,
        "tests": tests,
        "failed_tests": failed_tests,
        "numerical_pass": numerical_pass,
        "exceptional_obstruction": exceptional_obstruction,
        "status": status,
        "allowable": status == "allowable",
    }


def compact_configuration(record: dict[str, object]) -> dict[str, object]:
    return {
        "fibers": record["fibers"],
        "fiber_count": record["fiber_count"],
        "root_rank_sum": record["root_rank_sum"],
        "root_discriminant_product": record["root_discriminant_product"],
        "genus_drop_sum": record["genus_drop_sum"],
        "j_degree": record["j_degree"],
        "extra_ramification": record["extra_ramification"],
        "status": "allowable",
    }


def progress(message: str, enabled: bool) -> None:
    """Print a progress line to stderr when progress reporting is enabled."""
    if enabled:
        print(f"[classification] {message}", file=sys.stderr)


def derive(
    show_progress: bool = False,
    progress_every: int = 50,
    *,
    progress_enabled: bool | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Derive all configuration ledgers.

    ``progress_enabled`` is retained as a backward-compatible alias for
    ``show_progress`` because earlier tests and callers used that name.
    """
    if progress_enabled is not None:
        show_progress = progress_enabled
    records = []
    for index, fibers in enumerate(enumerate_euler_multisets(), 1):
        records.append(analyze_configuration(fibers))
        if progress_every > 0 and index % progress_every == 0:
            progress(f"analyzed {index} configurations", show_progress)
    progress(f"enumeration complete: {len(records)} configurations", show_progress)
    numerical = [record for record in records if record["numerical_pass"]]
    allowable_records = [record for record in records if record["allowable"]]
    exceptional = [
        record for record in records if record["status"] == "impossible_exceptional"
    ]

    status_counts = Counter(record["status"] for record in records)
    failed_test_counts = {
        test_name: sum(test_name in record["failed_tests"] for record in records)
        for test_name in (
            "constant_j_1_8",
            "extremal_square_1_5",
            "genus_drop_1_6",
            "hurwitz_1_11",
            "j_one_1_10",
            "j_zero_1_9",
            "picard_rank_1_4",
        )
    }

    four_raw = [record for record in records if record["fiber_count"] == 4]
    four_numerical = [record for record in four_raw if record["numerical_pass"]]
    four_allowable = [record for record in four_raw if record["allowable"]]
    four_nonconstant = [record for record in four_allowable if record["j_degree"] > 0]
    four_constant = [record for record in four_allowable if record["j_degree"] == 0]

    audit = {
        "source": SOURCE,
        "kodaira_table": KODAIRA_TABLE,
        "summary": {
            "raw_euler_sum_12": len(records),
            "numerically_admissible": len(numerical),
            "numerically_impossible": status_counts["impossible_numerical"],
            "exceptionally_impossible": len(exceptional),
            "allowable": len(allowable_records),
            "status_counts": {
                "impossible_numerical": status_counts["impossible_numerical"],
                "allowable": status_counts["allowable"],
                "impossible_exceptional": status_counts["impossible_exceptional"],
            },
            "failed_test_counts": failed_test_counts,
            "four_fibre": {
                "raw": len(four_raw),
                "numerically_admissible": len(four_numerical),
                "allowable": len(four_allowable),
                "allowable_nonconstant_J": len(four_nonconstant),
                "allowable_constant_J": len(four_constant),
                "constant_J_configurations": [
                    record["fibers"] for record in four_constant
                ],
            },
        },
        "configurations": records,
    }

    allowable = {
        "count": len(allowable_records),
        "configurations": [compact_configuration(record) for record in allowable_records],
    }
    four = {
        "count": len(four_allowable),
        "nonconstant_J_count": len(four_nonconstant),
        "constant_J_count": len(four_constant),
        "configurations": [compact_configuration(record) for record in four_allowable],
    }
    progress(
        "filters complete: "
        f"{len(numerical)} numerical, {len(allowable_records)} allowable",
        show_progress,
    )
    progress(
        "four-fibre slice complete: "
        f"{len(four_nonconstant)} nonconstant-J + "
        f"{len(four_constant)} constant-J",
        show_progress,
    )
    return audit, allowable, four


def report_text(audit: dict[str, object], four: dict[str, object]) -> str:
    summary = audit["summary"]
    four_summary = summary["four_fibre"]
    nonconstant = [row for row in four["configurations"] if row["j_degree"] > 0]
    exceptional = [
        row for row in audit["configurations"]
        if row["status"] == "impossible_exceptional"
    ]
    lines = [
        "# Miranda/Herfurtner configuration report",
        "",
        "## Reproduced database counts",
        "",
        f"- Euler-sum-12 multisets: **{summary['raw_euler_sum_12']}**.",
        f"- Numerically admissible after Miranda (1.3)-(1.11): **{summary['numerically_admissible']}**.",
        f"- Rejected by one or more numerical tests: **{summary['numerically_impossible']}**.",
        f"- Additional Table-(2.1) exceptional impossibilities: **{summary['exceptionally_impossible']}**.",
        f"- Allowable configurations: **{summary['allowable']}**.",
        "",
        "These exactly reproduce Miranda's 379 = 86 + 14 + 279 split.",
        "",
        "## Four-singular-fibre slice",
        "",
        f"- Raw four-fibre Euler partitions: **{four_summary['raw']}**.",
        f"- Numerically admissible: **{four_summary['numerically_admissible']}**.",
        f"- Allowable: **{four_summary['allowable']}**.",
        f"- Allowable with nonconstant J (the Herfurtner scope): **{four_summary['allowable_nonconstant_J']}**.",
        f"- Allowable with constant J: **{four_summary['allowable_constant_J']}**.",
        "",
        "The three constant-J four-fibre configurations are:",
        "",
    ]
    for fibers in four_summary["constant_J_configurations"]:
        lines.append(f"- `{' '.join(fibers)}`")
    lines.extend([
        "",
        "## Allowable nonconstant-J four-fibre configurations",
        "",
        "| # | Fibres | rank | disc. product | deg J | extra ramification |",
        "|---:|---|---:|---:|---:|---:|",
    ])
    for index, row in enumerate(nonconstant, 1):
        lines.append(
            f"| {index} | {' '.join(row['fibers'])} | {row['root_rank_sum']} | "
            f"{row['root_discriminant_product']} | {row['j_degree']} | "
            f"{row['extra_ramification']} |"
        )
    lines.extend([
        "",
        "## Role of the model solver",
        "",
        "The Weierstrass reconstruction and plane-Hamiltonian layers are not the enumerator.",
        "They are downstream realization certificates attached only after a fibre multiset",
        "survives this classification database.",
        "",
        "## Exceptional obstruction table",
        "",
        "| Miranda # | Fibres | reason |",
        "|---:|---|---|",
    ])
    for row in exceptional:
        obstruction = row["exceptional_obstruction"]
        lines.append(
            f"| {obstruction['table_number']} | {' '.join(row['fibers'])} | "
            f"{obstruction['reason']} |"
        )
    lines.append("")
    return "\n".join(lines)


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def output_map(
    show_progress: bool = False,
    progress_every: int = 50,
) -> dict[Path, object]:
    audit, allowable, four = derive(show_progress, progress_every)
    return {
        DATA_DIR / "configuration_audit_v2.json": audit,
        DATA_DIR / "allowable_configurations_v2.json": allowable,
        DATA_DIR / "four_fibre_allowable_v2.json": four,
        PAPER_DIR / "CONFIGURATION_REPORT.md": report_text(audit, four),
    }


def write_outputs(
    show_progress: bool = True,
    progress_every: int = 50,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    outputs = output_map(show_progress, progress_every)
    for path, value in outputs.items():
        if path.suffix == ".json":
            dump_json(path, value)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(value), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return derive(False, progress_every)


def check_outputs(
    show_progress: bool = True,
    progress_every: int = 50,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    expected_counts = {
        "raw_euler_sum_12": 379,
        "numerically_admissible": 293,
        "numerically_impossible": 86,
        "exceptionally_impossible": 14,
        "allowable": 279,
    }
    outputs = output_map(show_progress, progress_every)
    audit = outputs[DATA_DIR / "configuration_audit_v2.json"]
    for key, expected in expected_counts.items():
        actual = audit["summary"][key]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")
    four = audit["summary"]["four_fibre"]
    expected_four = {
        "raw": 85,
        "numerically_admissible": 69,
        "allowable": 59,
        "allowable_nonconstant_J": 56,
        "allowable_constant_J": 3,
    }
    for key, expected in expected_four.items():
        actual = four[key]
        if actual != expected:
            raise AssertionError(f"four_fibre.{key}: expected {expected}, got {actual}")

    for path, derived in outputs.items():
        if not path.exists():
            raise FileNotFoundError(
                f"missing checked-in output {path.relative_to(ROOT)}; run --write"
            )
        if path.suffix == ".json":
            retained = json.loads(path.read_text(encoding="utf-8"))
            if retained != derived:
                raise AssertionError(
                    f"derived data differs from {path.relative_to(ROOT)}; run --write and inspect"
                )
    print("classification: 379 -> 293 -> 279; four-fibre: 85 -> 69 -> 59 = 56+3")
    print("classification ledgers exactly match regenerated data")
    return (
        audit,
        outputs[DATA_DIR / "allowable_configurations_v2.json"],
        outputs[DATA_DIR / "four_fibre_allowable_v2.json"],
    )


def print_rows(title: str, rows: list[dict[str, object]]) -> None:
    """Print a named fiber set with every output line at most 80 columns."""
    print()
    print(f"{title} ({len(rows)})")
    for index, row in enumerate(rows, 1):
        fibers = " ".join(row["fibers"])
        suffix = ""
        if "status" in row and row["status"] != "allowable":
            suffix = f" [{row['status']}]"
        line = f"{index:03d}. {fibers}{suffix}"
        if len(line) > 80:
            raise AssertionError(f"printed line exceeds 80 columns: {line}")
        print(line)


def print_selected_set(
    audit: dict[str, object],
    allowable: dict[str, object],
    four: dict[str, object],
    *,
    selection: str,
) -> None:
    """Backward-compatible wrapper around :func:`print_set`."""
    print_set(selection, audit, allowable, four)


def print_set(
    mode: str,
    audit: dict[str, object],
    allowable: dict[str, object],
    four: dict[str, object],
) -> None:
    rows = four["configurations"]
    nonconstant = [row for row in rows if row["j_degree"] > 0]
    constant = [row for row in rows if row["j_degree"] == 0]
    if mode == "none":
        return
    if mode in ("four", "targets"):
        print_rows("Nonconstant-J four-fibre targets", nonconstant)
        if mode == "four":
            print_rows("Constant-J four-fibre cases", constant)
    elif mode == "allowable":
        print_rows("All allowable configurations", allowable["configurations"])
    elif mode == "audit":
        print_rows("All Euler-sum-12 configurations", audit["configurations"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write", action="store_true", help="regenerate all ledgers"
    )
    group.add_argument(
        "--check", action="store_true", help="compare derivation with ledgers"
    )
    parser.add_argument(
        "--print-set",
        choices=("four", "targets", "allowable", "audit", "none"),
        default="four",
        help="set to print after calculation (default: four)",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=50,
        help="report progress after this many configurations (default: 50)",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="suppress progress messages",
    )
    args = parser.parse_args()
    show_progress = not args.no_progress
    if args.write:
        audit, allowable, four = write_outputs(
            show_progress, args.progress_every
        )
    else:
        audit, allowable, four = check_outputs(
            show_progress, args.progress_every
        )
    print_set(args.print_set, audit, allowable, four)


if __name__ == "__main__":
    main()
