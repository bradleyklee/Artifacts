#!/usr/bin/env python3
"""Run the release-facing Apex 852 PDF proof test."""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
PDF = ROOT / "apex_and_chill_page13_v88_bottom_spacing.pdf"
SVG = ROOT / "data/v88_pdf_packet/artifact"
SVG = SVG / "apex_and_chill_page13_v88_bottom_spacing.svg"
CERT = ROOT / "data/v88_pdf_packet/certificate"
CERT = CERT / "apex852_pdf_payload_v88_reduced_certificate.json"
VISIBLE = ROOT / "build/generated/visible_pdf"
AUDIT = ROOT / "build/audit"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def say(msg: str) -> None:
    print(msg, flush=True)


def run(args: list[str], stdout: Path | None = None) -> None:
    cmd = [PY] + args
    if stdout is None:
        subprocess.run(cmd, cwd=ROOT, check=True)
    else:
        stdout.parent.mkdir(parents=True, exist_ok=True)
        with stdout.open("w") as f:
            subprocess.run(cmd, cwd=ROOT, stdout=f, check=True)


def assert_json(path: Path, *checks: str) -> None:
    run(["code/assert_json.py", "--quiet", rel(path), *checks])


def main() -> int:
    say("[TEST] dependency check")
    run(["code/check_deps.py"])

    say("[TEST] clean generated proof outputs")
    shutil.rmtree(VISIBLE, ignore_errors=True)
    for p in [
        AUDIT / "pdf_structure_check.json",
        AUDIT / "pdf_structure_check_stdout.json",
        AUDIT / "official_certificate_verify_stdout.json",
    ]:
        p.unlink(missing_ok=True)
    VISIBLE.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)

    say("[TEST] check PDF structure")
    run([
        "code/check_pdf_structure.py", rel(PDF),
        "--out-json", rel(AUDIT / "pdf_structure_check.json"),
    ], AUDIT / "pdf_structure_check_stdout.json")
    assert_json(
        AUDIT / "pdf_structure_check.json",
        "--eq", "ok", "true",
        "--eq", "pages", "1",
        "--eq", "image_xobjects", "0",
        "--ge", "uri_links", "1",
    )

    say("[TEST] extract visible/vector SVG data")
    run([
        "code/visible_svg_scrape_rederive_svgonly_v88_plus.py", rel(SVG),
        "--out-json", rel(VISIBLE / "visible_pdf_rederived_payload.json"),
        "--out-state", rel(VISIBLE / "visible_pdf_scraped_main_state.json"),
        "--out-report", rel(VISIBLE / "visible_pdf_rederive_report.json"),
        "--audit-payload-json", rel(CERT),
    ], VISIBLE / "visible_pdf_rederive_stdout.json")
    assert_json(
        VISIBLE / "visible_pdf_rederive_report.json",
        "--eq", "ok", "true",
        "--eq", "embedded_json_used", "false",
        "--eq", "matrix_unique_contexts", "536",
        "--eq", "matrix_counts.accept", "48",
        "--eq", "matrix_counts.reject", "41",
        "--eq", "independent_replay_from_rederived_payload.final_cells", "852",
        "--eq", "independent_replay_from_rederived_payload.last_history_row.births", "0",
        "--eq", "independent_replay_from_rederived_payload.unknown_terminal", "0",
        "--eq",
        "independent_replay_from_rederived_payload.compare_to_transformed_visible_main.exact",
        "true",
        "--eq", "audit_against_payload_json_not_used_for_derivation.accept_exact",
        "true",
        "--eq", "audit_against_payload_json_not_used_for_derivation.reject_exact",
        "true",
    )

    say("[TEST] verify derived certificate")
    run([
        "code/make_compatible_certificate_from_visible_payload.py",
        "--in-json", rel(VISIBLE / "visible_pdf_rederived_payload.json"),
        "--out-json",
        rel(VISIBLE / "visible_pdf_rederived_compatible_certificate.json"),
    ], VISIBLE / "visible_pdf_rederived_compatible_certificate_stdout.json")
    run([
        "code/verify_reduced_certificate_from_payload_v88.py", "--json",
        rel(VISIBLE / "visible_pdf_rederived_compatible_certificate.json"),
    ], VISIBLE / "visible_pdf_rederived_certificate_verify.json")
    assert_json(
        VISIBLE / "visible_pdf_rederived_certificate_verify.json",
        "--eq", "ok", "true",
        "--eq", "final_cells", "852",
        "--eq", "terminal_births", "0",
        "--eq", "terminal_unknown_frontier", "0",
        "--eq", "used_accept_rules", "48",
        "--eq", "used_reject_rules", "41",
        "--eq", "a_sequence_matches_payload", "true",
        "--eq", "first_differences_matches_payload", "true",
    )

    say("[TEST] verify official certificate")
    run([
        "code/verify_reduced_certificate_from_payload_v88.py", "--json",
        rel(CERT),
    ], AUDIT / "official_certificate_verify_stdout.json")
    assert_json(
        AUDIT / "official_certificate_verify_stdout.json",
        "--eq", "ok", "true",
        "--eq", "final_cells", "852",
        "--eq", "terminal_births", "0",
        "--eq", "terminal_unknown_frontier", "0",
        "--eq", "used_accept_rules", "48",
        "--eq", "used_reject_rules", "41",
    )

    say("[TEST] write 48-rule card")
    run([
        "code/print_rule_card.py",
        rel(VISIBLE / "visible_pdf_rederived_payload.json"),
        "--out-txt", rel(VISIBLE / "used_accept_rules_card.txt"),
        "--out-md", rel(VISIBLE / "used_accept_rules_card.md"),
    ], VISIBLE / "used_accept_rules_card_stdout.txt")

    say("")
    pdf = json.loads((AUDIT / "pdf_structure_check.json").read_text())
    vis = json.loads((VISIBLE / "visible_pdf_rederive_report.json").read_text())
    ver = json.loads((VISIBLE / "visible_pdf_rederived_certificate_verify.json").read_text())
    replay = vis["independent_replay_from_rederived_payload"]
    counts = vis["matrix_counts"]
    exact = replay["compare_to_transformed_visible_main"]["exact"]
    say("Apex 852 artifact test: PASS")
    say("-----------------------------------")
    def line(label: str, value) -> None:
        say(f"{label:<28} {value}")
    line("PDF pages:", pdf.get("pages"))
    line("PDF image XObjects:", pdf.get("image_xobjects"))
    line("PDF URI links:", pdf.get("uri_links"))
    line("Embedded JSON used:", vis.get("embedded_json_used"))
    line("Visible P7 contexts:", vis.get("matrix_unique_contexts"))
    line("Matrix accept/reject:", f"{counts.get('accept')}/{counts.get('reject')}")
    line("Matrix blank/pad:", f"{counts.get('blank')}/{counts.get('pad')}")
    line("SVG-derived cells:", replay.get("final_cells"))
    line("Terminal births:", replay.get("last_history_row", {}).get("births"))
    line("Unknown frontier:", replay.get("unknown_terminal"))
    line("Replay matches image:", exact)
    line("Derived verifier:", f"ok={ver.get('ok')} cells={ver.get('final_cells')}")
    line("Used accept/reject:", f"{ver.get('used_accept_rules')}/{ver.get('used_reject_rules')}")
    say("Rule card:")
    say("  build/generated/visible_pdf/used_accept_rules_card.txt")
    say("Detailed JSON logs:")
    say("  build/generated/visible_pdf/")
    say("  build/audit/")
    say("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
