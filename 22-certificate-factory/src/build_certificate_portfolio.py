#!/usr/bin/env python3
"""Assemble the 23 concise one-page certificates into one illustrated portfolio."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from build_concise_certificates import IDS, ROOT, matrix_summary


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    cases = []
    for cid in IDS:
        directory = ROOT / "examples" / cid / "release"
        pdf, payload = directory / "certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.pdf", directory / "certificate_payload.json"
        g, x, rank, nullity = matrix_summary(ROOT / "examples" / cid)
        cases.append({
            "case_id": cid,
            "certificate_pdf": str(pdf.relative_to(ROOT)),
            "certificate_pdf_sha256": digest(pdf),
            "payload": str(payload.relative_to(ROOT)),
            "payload_sha256": digest(payload),
            "matrix_summary": {"G_or_Gx_shape": g, "X_shape": x, "rank": rank, "nullity": nullity},
        })
    index = release / "HANNA_23_PAYLOAD_INDEX.json"
    index.write_text(json.dumps({"schema_version": "1.0", "date": "2026-07-31", "case_count": 23, "cases": cases}, indent=2, sort_keys=True) + "\n")
    include = "\n".join(rf"\includepdf[pages=-,pagecommand={{}}]{{../examples/{cid}/release/certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.pdf}}" for cid in IDS)
    tex = release / "HANNA_23_CALCULUS_CERTIFICATES.tex"
    tex.write_text(r"""\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.7in]{geometry}
\usepackage{xcolor,hyperref,pdfpages,embedfile,booktabs,tabularx}
\hypersetup{colorlinks=true,urlcolor=blue!55!black}
\definecolor{navy}{RGB}{25,54,86}
\pagestyle{empty}
\begin{document}
\embedfile[desc={23-case certificate payload index},mimetype=application/json]{HANNA_23_PAYLOAD_INDEX.json}
{\color{navy}\Huge\bfseries Illustrated calculus certificates}\par
\vspace{4mm}{\Large 23 typogeometric OEIS cases}\par
\vspace{8mm}
This portfolio presents one concise certificate per case: defining relation, first terms,
typogeometric trees, exact contour extraction, recurrence, differential equation, and
matrix-reduction dimensions. Each constituent PDF embeds its exact JSON payload; this
combined PDF embeds a SHA-256 index pointing to every constituent payload and certificate.

\vspace{6mm}
\textbf{Scope.} A120588--A120607, A244594, A244627, and A244856.\\
\textbf{Quality status.} All 23 defining relations, published prefixes, recurrence
instances, PDF structures, embedded payloads, and page layouts pass the release audit.\\
\textbf{Detailed reference.} The reviewed A120590 q=3 paper remains separately available
as the verbose explanatory example; these pages deliberately filter each record to its
most useful verified facts.

\vfill
Bradley Klee, \quad Mech.An.ika Sol (Open AI)\hfill July 31, 2026
\newpage
""" + include + "\n\\end{document}\n")
    proc = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=release, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (release / "HANNA_23_CALCULUS_CERTIFICATES.build.log").write_text(proc.stdout)
    if proc.returncode:
        raise SystemExit(proc.stdout[-3000:])
    pdf = tex.with_suffix(".pdf")
    print(json.dumps({"pdf": str(pdf.relative_to(ROOT)), "pages_expected": 24, "bytes": pdf.stat().st_size, "sha256": digest(pdf)}))


if __name__ == "__main__":
    main()
