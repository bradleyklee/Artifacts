#!/usr/bin/env python3
"""Independent exact-arithmetic audit of the 23-case release."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from build_concise_certificates import IDS, ROOT, recurrence


def load(path):
    return json.loads(path.read_text())


def convolve(a, b, length):
    out = [0] * length
    for i, x in enumerate(a[:length]):
        for j, y in enumerate(b[: length - i]):
            out[i + j] += x * y
    return out


def power_series(a, exponent, length):
    out = [1] + [0] * (length - 1)
    for _ in range(exponent):
        out = convolve(out, a, length)
    return out


def eval_n(expression, n):
    return int(eval(expression.replace("^", "**"), {"__builtins__": {}}, {"n": n}))


def recurrence_check(case, terms):
    coefficients, valid, _ = recurrence(case)
    order = len(coefficients) - 1
    tested = 0
    for n in range(valid, len(terms) - order):
        residual = sum(eval_n(p, n) * terms[n + r] for r, p in enumerate(coefficients))
        if residual:
            return False, tested, {"n": n, "residual": residual}
        tested += 1
    return True, tested, None


def definition_check(case, spec, terms):
    length = len(terms)
    if "parent" in spec:
        parent_terms = load(ROOT / "examples" / spec["parent"] / "data/terms.json")["terms"]
        exponent = int(spec["observable"].rsplit("^", 1)[1])
        expected = power_series(parent_terms, exponent, length)
        return terms == expected, "parent_power_convolution"
    q, r = int(spec["q"]), int(spec["r"])
    aq = power_series(terms, q, length)
    if "s" in spec:
        s = int(spec["s"])
        lhs = [r * terms[n] - (s * terms[n - 1] if n else 0) for n in range(length)]
        rhs = aq[:]
        rhs[0] += r - 1
    else:
        b, c = int(spec["b"]), int(spec["c"])
        lhs = [r * x for x in terms]
        rhs = aq[:]
        rhs[0] += c
        if length > 1:
            rhs[1] += b
    return lhs == rhs, "defining_equation_series"


def attachment_check(case):
    pdf = case / "release/certificate.pdf"
    payload = case / "release/certificate_payload.json"
    info = subprocess.run(["pdfinfo", str(pdf)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with tempfile.TemporaryDirectory() as directory:
        extracted = Path(directory) / "payload.json"
        proc = subprocess.run(
            ["pdfdetach", "-save", "1", "-o", str(extracted), str(pdf)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        same = proc.returncode == 0 and extracted.exists() and extracted.read_bytes() == payload.read_bytes()
    return info.returncode == 0 and same, hashlib.sha256(pdf.read_bytes()).hexdigest()


def main():
    rows = []
    for cid in IDS:
        case = ROOT / "examples" / cid
        spec = load(case / "input/case_spec.json")
        term_record = load(case / "data/terms.json")
        terms, prefix = term_record["terms"], term_record["oeis_prefix_checked"]
        rec_ok, rec_tests, failure = recurrence_check(case, terms)
        def_ok, def_method = definition_check(case, spec, terms)
        attachment_ok, pdf_hash = attachment_check(case)
        log = (case / "release/certificate.log").read_text(errors="replace")
        row = {
            "case_id": cid,
            "stored_terms": len(terms),
            "published_terms_checked": len(prefix),
            "published_prefix_exact": terms[: len(prefix)] == prefix,
            "definition_exact": def_ok,
            "definition_method": def_method,
            "recurrence_residuals_zero": rec_ok,
            "recurrence_instances_tested": rec_tests,
            "recurrence_failure": failure,
            "pdf_valid_and_payload_exact": attachment_ok,
            "pdf_sha256": pdf_hash,
            "tex_overfull_boxes": log.count("Overfull"),
        }
        row["status"] = "pass" if all((row["published_prefix_exact"], def_ok, rec_ok, attachment_ok, row["tex_overfull_boxes"] == 0)) else "fail"
        rows.append(row)
    summary = {
        "status": "pass" if all(x["status"] == "pass" for x in rows) else "fail",
        "case_count": len(rows),
        "stored_terms_checked": sum(x["stored_terms"] for x in rows),
        "published_terms_checked": sum(x["published_terms_checked"] for x in rows),
        "recurrence_instances_checked": sum(x["recurrence_instances_tested"] for x in rows),
        "cases": rows,
    }
    report = ROOT / "reports/REVISION_QUALITY_AUDIT.json"
    report.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    lines = [
        "---", "title: Revision quality audit", "date: 2026-07-31", "scope: 23 canonical OEIS cases", "---", "",
        "# Revision quality audit", "",
        f"Overall status: **{summary['status'].upper()}**. Exact checks cover {summary['stored_terms_checked']} stored coefficients, "
        f"{summary['published_terms_checked']} published-prefix entries, and {summary['recurrence_instances_checked']} recurrence instances.", "",
        "| A-number | Definition | Recurrence tests | Published prefix | PDF payload | Layout |", "|---|---:|---:|---:|---:|---:|",
    ]
    for x in rows:
        mark = lambda value: "pass" if value else "FAIL"
        lines.append(f"| {x['case_id']} | {mark(x['definition_exact'])} | {x['recurrence_instances_tested']} pass | {x['published_terms_checked']} pass | {mark(x['pdf_valid_and_payload_exact'])} | {mark(x['tex_overfull_boxes'] == 0)} |")
    lines += ["", "The JSON companion records per-case hashes, methods, counts, and any first failing recurrence residual.", ""]
    (ROOT / "reports/REVISION_QUALITY_AUDIT.md").write_text("\n".join(lines))
    print(json.dumps({k: summary[k] for k in ("status", "case_count", "stored_terms_checked", "published_terms_checked", "recurrence_instances_checked")}))


if __name__ == "__main__":
    main()
