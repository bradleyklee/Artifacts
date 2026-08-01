#!/usr/bin/env python3
"""Print the complete 23-case calculus evidence into one Markdown report."""
from __future__ import annotations

import hashlib
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_FILES = (
    "input/case_spec.json",
    "data/tree_model.json",
    "data/set_elements_n_le_3.json",
    "data/inverse_map.json",
    "data/coefficient_formula.json",
    "data/contour.json",
    "data/integrand_analysis.json",
    "data/matrices.json",
    "data/recurrence.json",
    "data/certificate.json",
    "data/ode.json",
    "data/terms.json",
    "checks/expectations.json",
    "checks/results.json",
    "manifest.json",
)


def load(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf-8"))


def block(label: str, obj) -> list[str]:
    return [
        f"### {label}",
        "",
        "```json",
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True),
        "```",
        "",
    ]


def main() -> None:
    targets = load(ROOT / "work/targets.json")
    ids = [item for family in targets["families"] for item in family["targets"]]
    assert len(ids) == 23 and len(set(ids)) == 23

    digest = (ROOT / "work/CALCULUS_DIGEST_23_CASES.md").read_text(
        encoding="utf-8"
    )
    lines = [
        "---",
        'title: "Full Calculus Evidence Report: 23 Hanna-Family Examples"',
        'artifact_type: "symbolic-computation evidence digest"',
        'schema_version: "1.0"',
        'generated_date: "2026-07-30"',
        'case_count: 23',
        'scope: "A120588–A120607, A244594, A244627, A244856"',
        'scope_status: "closed"',
        'case_state: "ANALYTIC_COMPLETE"',
        'arithmetic: "exact integer and rational"',
        'numerical_fitting: false',
        'published_source: "OEIS"',
        'generator: "src/generate_full_calculus_evidence.py"',
        'concise_companion: "work/CALCULUS_DIGEST_23_CASES.md"',
        'audit_record: "reports/full_calculus_evidence_audit.json"',
        "---",
        "",
        "# Full calculus evidence report: 23 Hanna-family examples",
        "",
        "## Purpose and evidentiary standard",
        "",
        "This is the expanded, machine-auditable companion to the concise calculus",
        "digest reproduced below. It prints the canonical mathematical payloads and",
        "the full derivation records for every one of the 23 specified OEIS cases.",
        "The report does not infer missing mathematics: every displayed object comes",
        "from a checked repository artifact.",
        "",
        "## Standard notation",
        "",
        "| Symbol | Meaning |",
        "|---|---|",
        r"| \(A(x)\) | algebraic ordinary generating function |",
        r"| \(T(x)\) | normalized shifted series, usually \(A(x)=1+cT(x)\) |",
        r"| \(x=\rho(u)\) | local inverse relation with \(u=T(x)\) |",
        r"| \(\gamma\) | small positively oriented contour around \(u=0\) |",
        r"| \(a_n=[x^n]A(x)\) | coefficient sequence |",
        r"| \(P_r(n)\) | polynomial multiplying shift \(a_{n+r}\) |",
        r"| \(G,U,V,J,X\) | exact reduction and remainder matrices |",
        r"| \(P_x\) | recurrence matrix: rows \(x^r\), columns \(n^k\) |",
        r"| \(\theta=x\,d/dx\) | Euler differential operator |",
        r"| \(R(n,u)\) | rational telescoping certificate |",
        "",
        "Human-facing formulas use these conventional symbols. JSON code blocks",
        "retain the exact source spelling required for deterministic regeneration.",
        "",
        "## Evidence chain",
        "",
        "For each case:",
        "",
        "1. `case_spec` fixes the algebraic series and normalization.",
        "2. `tree_model` gives the typogeometric grammar; `set_elements_n_le_3`",
        "   explicitly lists small objects and counts them.",
        "3. `inverse_map`, `coefficient_formula`, and `contour` derive coefficient",
        "   extraction from the algebraic relation.",
        "4. `integrand_analysis` identifies the rational integrand and reduction route.",
        "5. `matrices` records exact bases and matrices for Hermite/direct-x reduction.",
        "6. `recurrence` records the polynomial shift relation.",
        "7. `certificate` records the rational telescoper certificate.",
        "8. `ode` points to or contains the verified scalar linear differential equation.",
        "9. `terms` and `checks` compare exact generated coefficients with publication.",
        "10. `case.json` prints the complete derivation object, including intermediate",
        "    matrices, basis vectors, ODE reductions, and residual checks.",
        "",
        "All integers and rational functions below are printed exactly. The checks",
        "use symbolic identities and exact arithmetic, not floating-point fitting.",
        "",
        "## Core calculus used throughout",
        "",
        r"After writing the normalized algebraic solution as \(A(x)=1+cT(x)\),",
        r"the inverse relation has the form \(x=\rho(u)\) with \(u=T(x)\). Lagrange",
        "inversion gives coefficient extraction as a residue, equivalently a contour",
        "integral around the origin. For the primary cases the canonical form is",
        "",
        r"\[",
        r"a_n=\frac{c}{2\pi i\,n}\oint_\gamma\frac{du}{\rho(u)^n},",
        r"\qquad n\geq 1.",
        r"\]",
        "",
        r"Writing \(\rho(u)=uD(u)\), a shift \(n\mapsto n+r\) changes the pole order.",
        "Hermite reduction splits each shifted rational differential into an exact",
        "derivative plus a finite-dimensional remainder. The matrices `G`, `U`,",
        r"\(V\), and \(J\) encode that exact reduction; \(X\) collects remainder",
        r"vectors. A nonzero kernel vector of \(X\) supplies polynomials \(P_r(n)\)",
        "satisfying",
        "",
        r"\[",
        r"\sum_r P_r(n)a_{n+r}=0.",
        r"\]",
        "",
        "The rational object in `certificate.json` proves that the corresponding",
        "linear combination of integrands is an exact derivative, so its contour",
        "integral vanishes. Translating the recurrence with",
        "`theta = x*d/dx` produces the scalar linear ODE printed in the full",
        r"derivation. Descendant cases use the numerator-aware direct-\(x\)",
        "variant because differentiation introduces higher numerator powers.",
        "",
        "A120589 is exceptional: the seed already fills the full two-dimensional",
        "remainder space, so one additional shift is necessary. This is the recorded",
        "maximality observation. A244856 retains both the attached order-4 result and",
        "an independently derived order-5 cross-check; no minimality claim is made.",
        "",
        "## Concise digest",
        "",
        digest,
        "",
        "## Complete per-case payloads",
        "",
    ]

    inventory = []
    for case_id in ids:
        case_dir = ROOT / "examples" / case_id
        lines += [f"# {case_id}: complete evidence", ""]
        printed = []
        for rel in NORMALIZED_FILES:
            path = case_dir / rel
            assert path.exists(), path
            obj = load(path)
            lines += block(rel, obj)
            printed.append(
                {
                    "path": rel,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        case_json = case_dir / "case.json"
        if case_json.exists():
            derivation_paths = [case_json]
        else:
            derivation_paths = []
            for rel in NORMALIZED_FILES:
                wrapper = load(case_dir / rel)
                source = wrapper.get("canonical_source") if isinstance(wrapper, dict) else None
                if not source:
                    continue
                source_path = source.partition("#")[0]
                resolved = (
                    ROOT / source_path
                    if source_path.startswith("runs/")
                    else case_dir / source_path
                )
                if resolved not in derivation_paths:
                    derivation_paths.append(resolved)
            assert derivation_paths, f"No derivation payload found for {case_id}"
        for derivation_path in derivation_paths:
            assert derivation_path.exists(), derivation_path
            label_path = str(derivation_path.relative_to(ROOT))
            lines += block(f"{label_path} — full derivation payload", load(derivation_path))
            printed.append(
                {
                    "path": label_path,
                    "bytes": derivation_path.stat().st_size,
                    "sha256": hashlib.sha256(derivation_path.read_bytes()).hexdigest(),
                }
            )
        inventory.append({"case_id": case_id, "files": printed})

    lines += [
        "# Report inventory and integrity hashes",
        "",
        "The following JSON inventory identifies every source payload printed above.",
        "",
        "```json",
        json.dumps(
            {"case_count": len(ids), "cases": inventory},
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
    ]

    output = ROOT / "work/FULL_CALCULUS_EVIDENCE_23_CASES.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    audit = {
        "status": "verified",
        "case_count": len(ids),
        "a_number_headings": sum(
            1 for line in lines if line.startswith("# A") and ": complete evidence" in line
        ),
        "source_files_printed": sum(len(x["files"]) for x in inventory),
        "output": str(output.relative_to(ROOT)),
        "output_bytes": output.stat().st_size,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    (ROOT / "reports/full_calculus_evidence_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
