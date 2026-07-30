#!/usr/bin/env python3
"""Reproduce and cross-check the publication-facing q=3 packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import sympy as sp

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / ".support"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_tsv_matrix(path: Path) -> sp.Matrix:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append([sp.Rational(x) for x in line.split("\t")])
    return sp.Matrix(rows)


def check(condition: bool, name: str, records: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    records.append(f"PASS  {name}")


def main() -> None:
    records: list[str] = []
    q3 = load_module("packet_q3", ROOT / "ternatree_q3.py")
    result = q3.run_q3(30)
    n, x = result["n"], result["x"]
    terms = result["terms"]
    P = tuple(sp.expand(v) for v in result["P"])
    ode = tuple(sp.expand(v) for v in result["ode"])
    check(len(terms) == 31, "root executable returns a(0)..a(30)", records)

    case = json.loads((SUPPORT / "factory/case.json").read_text(encoding="utf-8"))
    factory_terms = [int(v) for v in case["terms"]]
    factory_P = tuple(sp.expand(sp.sympify(v)) for v in case["recurrence"])
    check(terms[:len(factory_terms)] == factory_terms,
          "root terms agree with frozen factory terms through n=24", records)
    check(P == factory_P, "root recurrence equals frozen factory recurrence", records)
    u = sp.symbols("u")
    expected_N = sp.sympify(case["certificate"]["N"])
    expected_R = sp.cancel(expected_N / sp.sympify(case["rho"]))
    check(sp.simplify(result["certificate"] - expected_R) == 0,
          "root certificate equals frozen factory certificate", records)

    validation = json.loads((SUPPORT / "factory/validation.json").read_text(encoding="utf-8"))
    check(validation["pass"] is True and validation["passed_checks"] == validation["total_checks"] == 65,
          "frozen factory validation is 65/65 PASS", records)

    expected_ode = (
        27*x**2 + 162*x - 13,
        27*(x + 3),
        -3,
    )
    check(tuple(sp.expand(a-b) for a,b in zip(ode, expected_ode)) == (0,0,0),
          "root ODE has the stated normalized coefficients", records)

    U = sp.Rational(1, 13) * sp.Matrix([[153,24,3],[72,9,6],[0,0,0]])
    V = sp.Rational(1, 13) * sp.Matrix([[-13,0,0],[75,11,3],[24,3,2]])
    J = sp.Matrix([[0,1,0],[0,0,2],[0,0,0]])
    check(U == parse_tsv_matrix(SUPPORT / "data/U.tsv"), "U.tsv equals executable U", records)
    check(V == parse_tsv_matrix(SUPPORT / "data/V.tsv"), "V.tsv equals executable V", records)
    check(J == parse_tsv_matrix(SUPPORT / "data/J.tsv"), "J.tsv equals executable J", records)

    claude = load_module("claude_literal", SUPPORT / "referees/claude/literal_translation.py")
    cr = claude.Q3(15)
    claude_terms = [int(cr["a"][k]) for k in range(16)]
    claude_P = tuple(sp.expand(cr[k]) for k in ("P0","P1","P2"))
    claude_ode = tuple(sp.expand(v) for v in cr["ODE"])
    check(claude_terms == terms[:16], "Claude literal translation terms agree through n=15", records)
    check(claude_P == P, "Claude literal translation recurrence agrees", records)
    check(claude_ode == ode, "Claude literal translation ODE agrees", records)

    kimi = load_module("kimi_corrected", SUPPORT / "referees/kimi-corrected/q3_algorithm.py")
    kt, kp, ko = kimi.Q3(30)
    kimi_P = tuple(sp.expand(v) for v in kp)
    kimi_ode = (
        sp.expand(ko.coeff(kimi.App_sym)),
        sp.expand(ko.coeff(kimi.Ap_sym)),
        sp.expand(ko.coeff(kimi.A_sym)),
    )
    check([int(v) for v in kt] == terms, "corrected Kimi terms agree through n=30", records)
    check(kimi_P == P, "corrected Kimi recurrence agrees", records)
    check(kimi_ode == ode or tuple(-v for v in kimi_ode) == ode,
          "corrected Kimi ODE agrees up to a global sign", records)

    graph_audit = (SUPPORT / "graphs/mystery_graph_audit.txt").read_text(encoding="utf-8")
    check("mystery_vertices 15" in graph_audit, "pseudocode graph exposes 15 mystery vertices", records)
    check("tree_depth 3" in graph_audit, "comparison graphics are shallow three-level trees", records)
    check("resolution_coverage PASS" in graph_audit and "python_evidence PASS" in graph_audit,
          "all mystery vertices have source-backed resolutions", records)

    required = [
        ROOT / "A120590_Ternatrees.pdf",
        ROOT / "ternatree_poetry_digest.pdf",
        ROOT / "ternatree_pseudocode_mysteries.png",
        ROOT / "ternatree_sympy_resolutions.png",
        SUPPORT / "source/A120590_ternatree_human.tex",
        SUPPORT / "source/ternatree_one_page_crank_academic.txt",
        SUPPORT / "source/ternatree_poetry_digest.tex",
        SUPPORT / "tools/make_mystery_comparison.py",
        SUPPORT / "graphs/ternatree_pseudocode_mysteries.pdf",
        SUPPORT / "graphs/ternatree_pseudocode_mysteries.svg",
        SUPPORT / "graphs/ternatree_sympy_resolutions.pdf",
        SUPPORT / "graphs/ternatree_sympy_resolutions.svg",
        SUPPORT / "payload/A120590_certificate_payload.json",
        SUPPORT / "payload/README.txt",
    ]
    check(all(p.is_file() and p.stat().st_size > 0 for p in required),
          "all publication and generation sources are present", records)

    nested = subprocess.run(
        ["sha256sum", "-c", "SHA256SUMS.txt"],
        cwd=SUPPORT / "factory", text=True, capture_output=True,
    )
    check(nested.returncode == 0, "nested factory checksum manifest is portable", records)

    pdfinfo = subprocess.run(
        ["pdfinfo", str(ROOT / "A120590_Ternatrees.pdf")],
        text=True, capture_output=True, check=True,
    ).stdout
    check("Pages:           16" in pdfinfo, "human-facing PDF has 16 portrait pages", records)

    paper_text = subprocess.run(
        ["pdftotext", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    check("Derivative reduction and the ODE" in paper_text,
          "paper includes a direct integral-to-ODE derivation", records)
    source_text = (SUPPORT / "source/A120590_ternatree_human.tex").read_text(encoding="utf-8")
    check("\\begin{equation" not in source_text and "\\label{" not in source_text and "\\eqref{" not in source_text,
          "paper source has no numbered equations or equation cross-references", records)
    check("residue" not in paper_text.lower() and "Res_{" not in source_text,
          "human paper consistently uses integral-form notation", records)
    order = [paper_text.find(title) for title in (
        "Trees, typogeometry, and contour integration",
        "Shift reduction and the recurrence",
        "Derivative reduction and the ODE",
        "Relations among the formulas",
        "Reference pseudocode",
        "Pseudocode operations and exact realization",
        "References by method",
    )]
    check(all(i >= 0 for i in order) and order == sorted(order),
          "paper sections occur in the intended geometric-to-computational order", records)
    check("G_x=G-xEE^T" in source_text and "G_0=G" in source_text,
          "paper explicitly compares G and G_x", records)
    check("\\log\\!\\left(1-\\frac{x}{\\rho(u)}\\right)" in source_text,
          "paper gives an integral definition of A(x)", records)
    check(source_text.find("Lars V. Ahlfors") < source_text.find("Aryeh Dvoretzky") < source_text.find(r"Fr\'ed\'eric Chyzak"),
          "bibliography orders complex calculus before combinatorics and symbolic reduction", records)
    check("The algebraic form is verified as an ansatz" in source_text and
          r"\widetilde A(x)=A(x)" in source_text,
          "algebraic equation is verified by the ODE ansatz and uniqueness", records)
    pseudo_text = (SUPPORT / "source/ternatree_one_page_crank_academic.txt").read_text(encoding="utf-8")
    check("exact certificate identity: PASS" in (SUPPORT / "validation/run_N30.txt").read_text(encoding="utf-8") and
          "R=C/rho" in pseudo_text and "certificate" in source_text.lower(),
          "paper, pseudocode, and executable include the exact certificate", records)
    check("Kimi (Moonshot AI)" in source_text and "Claude (Anthropic AI)" in source_text and
          "pseudocode and implementation presented in Sections 5--6" in source_text,
          "Appendix A attributes the merged one-shot implementations", records)
    check("Bradley Klee, \\quad Harm.On.ica S-O-L 5.6" in source_text and
          "OpenAI" in source_text,
          "title page carries the comma-separated author and company attribution", records)
    page4 = subprocess.run(
        ["pdftotext", "-f", "4", "-l", "4", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    page6 = subprocess.run(
        ["pdftotext", "-f", "6", "-l", "6", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    pages = {}
    for page_number in (8, 9, 10, 11):
        pages[page_number] = subprocess.run(
            ["pdftotext", "-f", str(page_number), "-l", str(page_number),
             str(ROOT / "A120590_Ternatrees.pdf"), "-"],
            text=True, capture_output=True, check=True,
        ).stdout
    check("Shift reduction and the recurrence" in page4,
          "shift-reduction section begins on page 4", records)
    check("Derivative reduction and the ODE" in page6,
          "derivative-reduction section begins on page 6", records)
    check("Relations among the formulas" in pages[8],
          "relations section begins on page 8", records)
    check("Reference pseudocode" in pages[9],
          "reference pseudocode is embedded on page 9", records)
    check("Pseudocode operations and exact realization" in pages[10],
          "comparison figure is embedded on page 10", records)
    check("References by method" in pages[11],
          "method-ordered bibliography begins on page 11", records)

    payload_path = SUPPORT / "payload/A120590_certificate_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    check(payload["schema"] == "a120590-human-certificate-payload-v1",
          "machine-readable payload has the declared schema", records)
    check(payload["pseudocode"]["text"] == (ROOT / "ternatree_one_page_crank.txt").read_text(encoding="utf-8"),
          "payload embeds the exact root pseudocode", records)
    check(payload["overview"]["initial_terms_a0_to_a30"] == terms,
          "payload terms agree with the executable through n=30", records)
    for name, expected in (("G", parse_tsv_matrix(SUPPORT / "data/G.tsv")),
                           ("U", U), ("V", V), ("J", J)):
        observed = sp.Matrix([[sp.sympify(e) for e in row]
                              for row in payload["exact_data"]["matrices"][name]["entries"]])
        check(observed == expected, f"payload matrix {name} is exact", records)
    check(payload["checks"]["factory_validation_summary"]["passed"] == 65 and
          all(item["status"] == "pass" for item in payload["checks"]["assertions"]),
          "payload exposes semantic PASS records for the principal checks", records)
    reference_methods = [r["method"] for r in payload["references"]]
    check(reference_methods[:3] == ["complex calculus", "applied complex calculus", "Lagrange inversion"],
          "payload references put calculus and inversion first", records)

    output = [
        "A120590 TERNATREE PACKET AUDIT",
        f"root {ROOT}",
        f"root_python_sha256 {hashlib.sha256((ROOT / 'ternatree_q3.py').read_bytes()).hexdigest()}",
        f"checks {len(records)}/{len(records)} PASS",
        "",
        *records,
        "",
        "SCOPE",
        "The packet is self-contained for the human PDF, compact JSON reading payload,",
        "sequence generation, recurrence, ODE, and cross-checks against the frozen",
        "q=3 factory case. The general multi-q RELAY factory generator is not copied",
        "into this sequence-specific publication packet; its frozen q=3 outputs and",
        "independent 65/65 validation record are included under .support/factory/.",
    ]
    print("\n".join(output))


if __name__ == "__main__":
    main()
