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
        SUPPORT / "source/A120590_ternatree_derivation_v13.tex",
        SUPPORT / "source/ternatree_one_page_crank_academic.txt",
        SUPPORT / "source/ternatree_poetry_digest.tex",
        SUPPORT / "tools/make_mystery_comparison.py",
        SUPPORT / "graphs/ternatree_pseudocode_mysteries.pdf",
        SUPPORT / "graphs/ternatree_pseudocode_mysteries.svg",
        SUPPORT / "graphs/ternatree_sympy_resolutions.pdf",
        SUPPORT / "graphs/ternatree_sympy_resolutions.svg",
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
    check("Pages:           13" in pdfinfo, "human-facing PDF has 13 portrait pages", records)

    paper_text = subprocess.run(
        ["pdftotext", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    check("Direct reduction in the generating variable" in paper_text,
          "paper includes a direct integral-to-ODE derivation", records)
    source_text = (SUPPORT / "source/A120590_ternatree_derivation_v13.tex").read_text(encoding="utf-8")
    check("\\begin{equation" not in source_text and "\\label{" not in source_text and "\\eqref{" not in source_text,
          "paper source has no numbered equations or equation cross-references", records)
    check("residue" not in paper_text.lower() and "Res_{" not in source_text,
          "human paper consistently uses integral-form notation", records)
    order = [paper_text.find(title) for title in (
        "From ternatrees to the integral form",
        "Shift reduction and the recurrence",
        "Direct reduction in the generating variable",
        "Comparison of the two reductions",
    )]
    check(all(i >= 0 for i in order) and order == sorted(order),
          "mathematical sections occur in geometric, shift, direct, comparison order", records)
    check("G_x=G-x" in source_text and "G_x\\big|_{x=0}=G" in source_text,
          "paper explicitly compares G and G_x", records)
    check("\\log\\!\\left(1-\\frac{x}{\\rho(u)}\\right)" in source_text,
          "paper gives an integral definition of A(x)", records)
    check("A'(x)=\\frac{1}{Q(x,T(x))}" in source_text and "A(x)=1+T(x)" in source_text,
          "algebraic equation is derived from the generating-function integral", records)
    check("Kimi (Moonshot AI)" in source_text and "Claude (Anthropic AI)" in source_text and
          "pseudocode presented in Section 5" in source_text,
          "Appendix A attributes the merged one-shot implementations", records)
    check("Bradley Klee, \\quad Harm.On.ica S-O-L 5.6" in source_text and
          "OpenAI" in source_text,
          "title page carries the comma-separated author and company attribution", records)
    page4 = subprocess.run(
        ["pdftotext", "-f", "4", "-l", "4", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    page5 = subprocess.run(
        ["pdftotext", "-f", "5", "-l", "5", str(ROOT / "A120590_Ternatrees.pdf"), "-"],
        text=True, capture_output=True, check=True,
    ).stdout
    check("Shift reduction and the recurrence" in page4 and
          "Direct reduction in the generating variable" not in page4,
          "Section 2 occupies its own page", records)
    check("Direct reduction in the generating variable" in page5 and "G =" in page5,
          "Section 3 opens with the fixed G matrix", records)

    output = [
        "A120590 TERNATREE PACKET AUDIT",
        f"root {ROOT}",
        f"root_python_sha256 {hashlib.sha256((ROOT / 'ternatree_q3.py').read_bytes()).hexdigest()}",
        f"checks {len(records)}/{len(records)} PASS",
        "",
        *records,
        "",
        "SCOPE",
        "The packet is self-contained for the human PDF, graph regeneration,",
        "sequence generation, recurrence, ODE, and cross-checks against the frozen",
        "q=3 factory case. The general multi-q RELAY factory generator is not copied",
        "into this sequence-specific publication packet; its frozen q=3 outputs and",
        "independent 65/65 validation record are included under .support/factory/.",
    ]
    print("\n".join(output))


if __name__ == "__main__":
    main()
