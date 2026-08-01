#!/usr/bin/env python3
"""Mechanical OEIS style checks for the canonical paste-ready delta file."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "work/OEIS_FIELD_ADDITIONS_23_CASES.txt"
REPORT = ROOT / "reports/oeis_style_audit.json"


def main():
    targets = json.loads((ROOT / "work/targets.json").read_text())
    ids = [item for family in targets["families"] for item in family["targets"]]
    content = TEXT.read_text()
    all_lines = content.splitlines()
    fields = [line for line in all_lines if re.match(r"^%[FCeH] A\d{6} ", line)]
    findings = []

    def flag(rule, line_number, text):
        findings.append({"rule": rule, "line": line_number, "text": text})

    if re.findall(r"^# (A\d{6})$", content, re.M) != ids:
        flag("target_order_or_coverage", 0, "A-number headings do not equal work/targets.json")
    for number, line in enumerate(all_lines, 1):
        if any(ord(char) > 127 for char in line):
            flag("non_ascii_mathematical_text", number, line)
        if "**" in line:
            flag("exponentiation_must_use_caret", number, line)
        if re.search(r"\\(?:ge|geq|le|leq|ne|neq)\b|[≤≥≠±×·…]", line):
            flag("nonpreferred_symbol", number, line)
        if re.search(r"\b\d+ x \d+\b", line):
            flag("matrix_dimension_must_use_capital_X", number, line)
        if re.search(r"\bd/n\b|\bE\(u\)", line):
            flag("undefined_symbol", number, line)
        if "(0)*" in line:
            flag("redundant_zero_term", number, line)
        if line.startswith(("%F ", "%C ", "%e ")) and not line.endswith(". - ~~~~"):
            flag("contribution_must_be_signed_after_period", number, line)
        if line.startswith("%H ") and ("Open AI" in line or "Mech.An.ika" in line):
            flag("ai_must_not_be_link_author", number, line)

    for case_id in ids:
        if len(re.findall(rf"^%H {case_id} Bradley Klee, ", content, re.M)) != 1:
            flag("one_human_authored_certificate_link_per_case", 0, case_id)

    report = {
        "status": "pass" if not findings else "fail",
        "style_sheet_checked": "2026-07-31",
        "a120590_live_draft_revision_checked": 31,
        "case_count": len(ids),
        "field_line_count": len(fields),
        "signed_formula_comment_example_lines": sum(
            line.startswith(("%F ", "%C ", "%e ")) and line.endswith(". - ~~~~")
            for line in fields
        ),
        "link_lines": sum(line.startswith("%H ") for line in fields),
        "findings": findings,
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "case_count", "field_line_count", "signed_formula_comment_example_lines", "link_lines")}, sort_keys=True))
    raise SystemExit(0 if not findings else 1)


if __name__ == "__main__":
    main()
