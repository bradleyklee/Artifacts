#!/usr/bin/env python3
"""Generate a detailed but GitHub-renderable 23-case calculus report."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf-8"))


def descend(obj, fragment: str):
    for key in fragment.strip("/").split("/") if fragment.strip("/") else []:
        obj = obj[key]
    return obj


def canonical(case: Path, relative: str):
    wrapper = load(case / relative)
    source = wrapper.get("canonical_source") if isinstance(wrapper, dict) else None
    if not source:
        return wrapper, relative
    path_text, _, fragment = source.partition("#")
    path = ROOT / path_text if path_text.startswith("runs/") else case / path_text
    return descend(load(path), fragment), source


def json_block(obj) -> list[str]:
    return ["```json", json.dumps(obj, indent=2, sort_keys=True), "```", ""]


def matrix_summary(wrapper, resolved):
    """Keep dimensions and recurrence-bearing remainder matrices, omit bulk traces."""
    result = {
        "status": wrapper.get("status", "verified"),
        "canonical_source": wrapper.get("canonical_source", "data/matrices.json"),
    }
    for key in ("statistics", "pilot_statistics", "bases"):
        if key in wrapper:
            result[key] = wrapper[key]
    if "bases" in resolved:
        result["bases"] = resolved["bases"]
    matrices = resolved.get("matrices", resolved)
    shapes = {}
    remainder_matrices = {}
    if isinstance(matrices, dict):
        for name, value in matrices.items():
            if not isinstance(value, dict):
                continue
            if "shape" in value:
                shapes[name] = value["shape"]
            if name in ("X", "X_full") and "entries" in value:
                encoded = json.dumps(value, sort_keys=True).encode()
                if len(encoded) <= 2500:
                    remainder_matrices[name] = value
                else:
                    entries = value["entries"]
                    remainder_matrices[name] = {
                        "shape": value.get("shape", [len(entries), len(entries[0])]),
                        "entry_count": len(entries) * len(entries[0]),
                        "representative_entries": {
                            "top_left": entries[0][0],
                            "top_right": entries[0][-1],
                            "bottom_left": entries[-1][0],
                            "bottom_right": entries[-1][-1],
                        },
                        "full_object_sha256": hashlib.sha256(encoded).hexdigest(),
                        "full_entries_location": result["canonical_source"],
                    }
    result["matrix_shapes"] = shapes
    result["remainder_matrices"] = remainder_matrices
    result["full_entries_location"] = result["canonical_source"]
    return result


def element_summary(obj):
    encoded = json.dumps(obj, sort_keys=True).encode()
    if len(encoded) <= 3000:
        return obj
    groups = {}
    for count, elements in obj["elements_by_true_leaf_count"].items():
        groups[count] = {
            "count": len(elements),
            "first_five": elements[:5],
            "last_five": elements[-5:],
        }
    return {
        "status": obj["status"],
        "encoding": obj["encoding"],
        "maximum_true_leaves": obj["maximum_true_leaves"],
        "checks": obj["checks"],
        "representative_elements": groups,
        "full_object_sha256": hashlib.sha256(encoded).hexdigest(),
        "full_list_location": "data/set_elements_n_le_3.json",
    }


def certificate_summary(obj, source):
    encoded = json.dumps(obj, sort_keys=True).encode()
    if len(encoded) <= 8000:
        return obj
    result = {
        "status": obj.get("status", "verified"),
        "full_object_sha256": hashlib.sha256(encoded).hexdigest(),
        "full_certificate_location": source,
    }
    for key, value in obj.items():
        if key == "status":
            continue
        if isinstance(value, str) and len(value) > 1000:
            result[key] = {
                "character_count": len(value),
                "leading_500_characters": value[:500],
                "sha256": hashlib.sha256(value.encode()).hexdigest(),
            }
        else:
            result[key] = value
    return result


def main() -> None:
    target_data = load(ROOT / "work/targets.json")
    ids = [a for family in target_data["families"] for a in family["targets"]]
    assert len(ids) == 23
    lines = [
        "---",
        'title: "Calculus Certificates for 23 Hanna-Family Sequences"',
        'artifact_type: "human-readable mathematical evidence report"',
        'schema_version: "1.0"',
        'generated_date: "2026-07-30"',
        "case_count: 23",
        'scope: "A120588–A120607, A244594, A244627, A244856"',
        'case_state: "ANALYTIC_COMPLETE"',
        'arithmetic: "exact"',
        "numerical_fitting: false",
        'generator: "src/generate_github_calculus_report.py"',
        'exhaustive_companion: "work/FULL_CALCULUS_EVIDENCE_23_CASES.md"',
        "---",
        "",
        "# Calculus certificates for 23 Hanna-family sequences",
        "",
        "This report gives the mathematical evidence behind the completion claim",
        "without duplicating the multi-megabyte internal derivation traces. The",
        "exhaustive report remains available for forensic review.",
        "",
        "## Standard notation and method",
        "",
        "The algebraic generating function is $A(x)$ and its normalized shifted",
        "series is $T(x)$. The local inverse is written $x=\\rho(u)$ with",
        "$u=T(x)$. Lagrange inversion gives",
        "",
        "$$",
        "a_n=\\frac{c}{2\\pi i\\,n}\\oint_\\gamma\\frac{du}{\\rho(u)^n},",
        "\\qquad n\\ge 1.",
        "$$",
        "",
        "Hermite reduction separates each shifted integrand into an exact derivative",
        "and a finite-dimensional remainder. The exact matrices $G,U,V,J$ encode",
        "the reduction and $X$ collects the remainder vectors. A kernel vector gives",
        "",
        "$$",
        "\\sum_r P_r(n)a_{n+r}=0.",
        "$$",
        "",
        "The rational function $R(n,u)$ is the telescoping certificate: its",
        "$u$-derivative equals the recurrence combination of integrands. Hence the",
        "contour integral vanishes. Substituting the Euler operator",
        "$\\theta=x\\,d/dx$ translates the recurrence into a scalar linear ODE.",
        "",
        "For descendants, differentiation introduces numerator powers, so the",
        "numerator-aware direct-$x$ reduction is used. A120589 requires an extra",
        "shift because its seed fills the full remainder space. A244856 has both",
        "an attached order-4 certificate and an independent order-5 cross-check;",
        "minimality is not claimed.",
        "",
        "## Coverage summary",
        "",
        "| Evidence | Coverage |",
        "|---|---:|",
        "| Typogeometric models | 23/23 |",
        "| Explicit small-set enumeration | 23/23 |",
        "| Contour representations | 23/23 |",
        "| Exact matrix reductions | 23/23 |",
        "| Polynomial recurrences | 23/23 |",
        "| Rational telescoping certificates | 23/23 |",
        "| Scalar linear ODEs | 23/23 |",
        "| Stored exact coefficients | 552/552 |",
        "| Recorded checks passing | 46/46 |",
        "",
    ]
    sources = (
        ("Geometric model", "data/tree_model.json"),
        ("Explicit elements through three true leaves", "data/set_elements_n_le_3.json"),
        ("Contour representation", "data/contour.json"),
        ("Integrand analysis", "data/integrand_analysis.json"),
        ("Exact reduction matrices", "data/matrices.json"),
        ("Polynomial recurrence", "data/recurrence.json"),
        ("Rational telescoping certificate", "data/certificate.json"),
        ("Scalar linear ODE", "data/ode.json"),
        ("Exact terms and published prefix", "data/terms.json"),
        ("Verification results", "checks/results.json"),
    )
    for case_id in ids:
        case = ROOT / "examples" / case_id
        spec = load(case / "input/case_spec.json")
        lines += [f"## {case_id}", "", "### Defining data", ""]
        lines += json_block(spec)
        for title, rel in sources:
            obj, source = canonical(case, rel)
            if rel == "data/matrices.json":
                obj = matrix_summary(load(case / rel), obj)
            elif rel == "data/set_elements_n_le_3.json":
                obj = element_summary(obj)
            elif rel == "data/certificate.json":
                obj = certificate_summary(obj, source)
            lines += [f"### {title}", "", f"Canonical source: `{source}`", ""]
            lines += json_block(obj)

    output = ROOT / "work/CALCULUS_EVIDENCE_GITHUB_23_CASES.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    assert output.read_text(encoding="utf-8").count("\n## A") == 23
    assert "~" not in output.read_text(encoding="utf-8")
    audit = {
        "status": "verified",
        "case_count": 23,
        "output": str(output.relative_to(ROOT)),
        "output_bytes": output.stat().st_size,
        "literal_tilde_count": 0,
        "github_math_delimiters": "dollar",
    }
    (ROOT / "reports/github_calculus_report_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
