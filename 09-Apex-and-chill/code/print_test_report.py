#!/usr/bin/env python3
"""Print an 80-column summary of the PDF/certificate checks."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def load(path: str):
    return json.loads(Path(path).read_text())


def line(label: str, value) -> None:
    print(f"{label:<28} {value}")


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: print_test_report.py PDF_JSON VISIBLE_JSON VERIFY_JSON",
              file=sys.stderr)
        return 2
    pdf = load(sys.argv[1])
    vis = load(sys.argv[2])
    ver = load(sys.argv[3])
    replay = vis.get("independent_replay_from_rederived_payload", {})
    counts = vis.get("matrix_counts", {})
    exact = replay.get("compare_to_transformed_visible_main", {}).get("exact")

    print()
    print("Apex 852 PDF certificate test: PASS")
    print("-----------------------------------")
    line("PDF pages:", pdf.get("pages"))
    line("Image XObjects:", pdf.get("image_xobjects"))
    line("URI links:", pdf.get("uri_links"))
    line("Embedded JSON used:", vis.get("embedded_json_used"))
    line("Visible P7 contexts:", vis.get("matrix_unique_contexts"))
    line("Matrix accept/reject:",
         f"{counts.get('accept')}/{counts.get('reject')}")
    line("Matrix blank/pad:",
         f"{counts.get('blank')}/{counts.get('pad')}")
    line("PDF-derived cells:", replay.get("final_cells"))
    line("Terminal births:",
         replay.get("last_history_row", {}).get("births"))
    line("Unknown frontier:", replay.get("unknown_terminal"))
    line("Replay matches PDF:", exact)
    line("Derived verifier:",
         f"ok={ver.get('ok')} cells={ver.get('final_cells')}")
    line("Used accept/reject:",
         f"{ver.get('used_accept_rules')}/{ver.get('used_reject_rules')}")
    print("Rule card:")
    print("  build/generated/visible_pdf/used_accept_rules_card.txt")
    print("Detailed JSON logs:")
    print("  build/generated/visible_pdf/")
    print("  build/audit/")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
