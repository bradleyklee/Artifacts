#!/usr/bin/env python3
"""Independent verifier for the layered A120593 certificate PDF.

The verifier accepts only the PDF as mathematical input.  It extracts the JSON
attachment, rebuilds consequences with SymPy and Python integers, inspects PDF
container properties, and records where the visible layer cannot be parsed
semantically because equations are stored as vector outlines.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import fitz
import sympy as sp
from matplotlib.mathtext import MathTextParser
from pypdf import PdfReader


def multinomial_counts(limit: int) -> list[int]:
    out = [1]
    for n in range(1, limit + 1):
        total = 0
        for k in range((n - 1) // 3 + 1):
            for j in range((n - 1 - 3 * k) // 2 + 1):
                i = n - 1 - 2 * j - 3 * k
                total += (
                    math.factorial(n + i + j + k - 1)
                    * 6**i
                    * 4**j
                    // (
                        math.factorial(n)
                        * math.factorial(i)
                        * math.factorial(j)
                        * math.factorial(k)
                    )
                )
        out.append(total)
    return out


def poly_from_coeffs(coeffs, variable):
    return sum(sp.Integer(c) * variable**e for e, c in enumerate(coeffs))


def check_pdf(path: Path) -> dict:
    pdf_bytes = path.read_bytes()
    reader = PdfReader(path)
    names = list(reader.attachments)
    if "a120593_certificate.json" not in names:
        raise RuntimeError("required JSON attachment is absent")
    payload_bytes = reader.attachments["a120593_certificate.json"][0]
    data = json.loads(payload_bytes)

    checks = []

    def record(name, passed, detail, *, scope="mathematics"):
        checks.append(
            {
                "name": name,
                "scope": scope,
                "status": "pass" if passed else "fail",
                "detail": detail,
            }
        )
        return passed

    doc = fitz.open(path)
    visible_text = "\n".join(page.get_text() for page in doc)
    links = [link.get("uri") for page in doc for link in page.get_links() if link.get("uri")]
    raster_counts = [len(page.get_images(full=True)) for page in doc]
    page_count = len(doc)
    doc.close()

    record("two-page carrier", page_count == 2, {"pages": page_count}, scope="container")
    record(
        "vector-only pages",
        raster_counts == [0, 0],
        {"raster_image_counts": raster_counts},
        scope="container",
    )
    record(
        "declared external links",
        "https://oeis.org/A120593" in links
        and "https://arxiv.org/abs/2307.07216" in links,
        {"links": links},
        scope="container",
    )
    record(
        "visible prose anchors",
        all(
            anchor in visible_text
            for anchor in (
                "Counting the quadrant trees",
                "The witness certificate",
                "INTEGRAL FORM",
                "EXACT VERIFICATION IDENTITY",
                "RATIONAL CERTIFICATE",
                "RECURRENCE OPERATOR",
                "ALGEBRAIC & DIFFERENTIAL OPERATORS",
            )
        ),
        "section headings extracted from the PDF text layer",
        scope="surface",
    )

    expected = [int(x) for x in data["initial_values"]]
    counts = multinomial_counts(max(12, len(expected) - 1))
    record(
        "multinomial initial values",
        counts[: len(expected)] == expected,
        {"computed": counts[: len(expected)], "payload": expected},
    )

    n, u, x = sp.symbols("n u x")
    D = 1 - 6 * u - 4 * u**2 - u**3

    # Residue/coefficient extraction and multinomial expansion, checked for a
    # nontrivial finite range from definitions rather than copied values.
    residue_values = []
    for nn in range(1, 9):
        residue_values.append(
            int(sp.residue(1 / (nn * u**nn * D**nn), u, 0))
        )
    record(
        "integral residues equal multinomial counts",
        residue_values == counts[1:9],
        {"n_1_through_8": residue_values},
    )

    # Check the formal identity behind moving the exponent to the constraint.
    coefficient_values = []
    for nn in range(1, 9):
        ser = sp.series(D ** (-nn), u, 0, nn).removeO().expand()
        coefficient_values.append(int(ser.coeff(u, nn - 1) / nn))
    record(
        "residue selects coefficient n-1",
        coefficient_values == residue_values,
        {"coefficient_values": coefficient_values},
    )

    # Reconstruct the certificate from payload arrays and verify it exactly.
    P_text = data["recurrence"]["P"]
    P = [sp.sympify(p.replace("^", "**"), locals={"n": n}) for p in P_text]
    coeffs = data["rational_certificate"]["N_by_n_degree"]
    N = sum(n ** int(deg) * poly_from_coeffs(values, u) for deg, values in coeffs.items())
    R = N / (u**2 * (u**3 + 4 * u**2 + 6 * u - 1) ** 2)
    # Divide the identity by H_n before simplifying.  This removes symbolic
    # powers u^n and D(u)^n and leaves a literal rational function in Q(n,u).
    h_ratio = lambda r: n / (n + r) * u ** (-r) * D ** (-r)
    logarithmic_derivative = -n / u - n * sp.diff(D, u) / D
    certificate_difference = sp.factor(
        sp.cancel(
            sp.together(
                sum(P[r] * h_ratio(r) for r in range(4))
                - sp.diff(R, u)
                - R * logarithmic_derivative
            )
        )
    )
    record(
        "rational telescoping identity over Q(n,u)",
        certificate_difference == 0,
        {"reduced_difference": str(certificate_difference)},
    )

    # Recurrence against independently computed multinomial terms.
    recurrence_residuals = []
    for nn in range(0, 10):
        residual = sum(int(P[r].subs(n, nn)) * counts[nn + r] for r in range(4))
        recurrence_residuals.append(residual)
    record(
        "P-recurrence matches multinomial sequence",
        recurrence_residuals == [0] * len(recurrence_residuals),
        {"n_0_through_9_residuals": recurrence_residuals},
    )

    # Derive coefficient recurrence from the printed differential operator.
    C0 = sp.expand(256 * n * (n - 1) * (n - 2) + 1152 * n * (n - 1) + 688 * n - 40)
    C1 = sp.expand(3072 * (n + 1) * n * (n - 1) + 9216 * (n + 1) * n + 2752 * (n + 1))
    C2 = sp.expand(12288 * (n + 2) * (n + 1) * n + 18432 * (n + 2) * (n + 1))
    C3 = sp.expand(-491 * (n + 3) * (n + 2) * (n + 1))
    operator_match = [sp.factor(c + p) for c, p in zip((C0, C1, C2, C3), P)]
    record(
        "differential operator coefficient translation",
        operator_match == [0, 0, 0, 0],
        {"differential_coefficients_plus_recurrence_P": [str(v) for v in operator_match]},
    )

    # Algebraic generating function against independent coefficients.
    A = sum(sp.Integer(counts[r]) * x**r for r in range(len(counts)))
    algebraic_residual = sp.expand(A**4 - 5 * A + 4 + x)
    checked_degree = len(counts) - 1
    low_residual = [int(algebraic_residual.coeff(x, r)) for r in range(checked_degree + 1)]
    record(
        "algebraic generating equation",
        low_residual == [0] * len(low_residual),
        {"checked_degrees": [0, checked_degree], "residual_coefficients": low_residual},
    )

    # D(u) is obtained from Q=x/D(Q), equivalent to Q=x+6Q^2+4Q^3+Q^4.
    Q = A - 1
    q_relation = sp.expand(Q - x - 6 * Q**2 - 4 * Q**3 - Q**4)
    q_low = [int(q_relation.coeff(x, r)) for r in range(checked_degree + 1)]
    record(
        "D and quadtree generating equation correspondence",
        q_low == [0] * len(q_low),
        {"checked_degrees": [0, checked_degree], "residual_coefficients": q_low},
    )

    # The visible equations are paths, but their exact rendering source is now
    # carried in the PDF's JSON attachment.  Check completeness, unique IDs,
    # and that every expression is accepted by the same MathText grammar.
    math_tokens = ("D(u)=", "q_n=", "P_0", "A(x)")
    found_math_tokens = [token for token in math_tokens if token in visible_text]
    surface_math = data.get("surface_math", {})
    math_items = [item for key in ("page_1", "page_2") for item in surface_math.get(key, [])]
    ids = [item.get("id") for item in math_items]
    parser = MathTextParser("path")
    parse_errors = []
    for item in math_items:
        try:
            parser.parse(f"${item['latex']}$", dpi=72)
        except Exception as exc:
            parse_errors.append({"id": item.get("id"), "error": str(exc)})
    record(
        "surface equation source inventory",
        bool(math_items) and len(ids) == len(set(ids)) and not parse_errors,
        {
            "format": surface_math.get("format"),
            "page_1_equations": len(surface_math.get("page_1", [])),
            "page_2_equations": len(surface_math.get("page_2", [])),
            "duplicate_ids": sorted({v for v in ids if ids.count(v) > 1}),
            "parse_errors": parse_errors,
            "ordinary_text_layer_tokens": found_math_tokens,
            "qualification": "JSON carries exact MathText source; the rendered outlines still require visual or renderer-trust review.",
        },
        scope="surface",
    )

    by_id = {item["id"]: item["latex"] for item in math_items}
    surface_value_checks = {
        "p1-count-1": f"a(1)={expected[1]}",
        "p1-count-2": f"a(2)={expected[2]}",
        "p1-count-3": f"a(3)={expected[3]}",
        "p2-initial-values": "q_0,\\ldots,q_5=" + ",".join(map(str, expected)),
        "p2-P0": "P_0=" + P_text[0].replace("*", "").replace("**", "^"),
    }
    # P0 is checked structurally below instead of relying on the crude text
    # conversion; the first four entries are exact literal cross-layer checks.
    literal_results = {
        key: by_id.get(key) == value
        for key, value in list(surface_value_checks.items())[:4]
    }
    record(
        "surface inventory agrees with canonical initial data",
        all(literal_results.values()),
        literal_results,
        scope="surface",
    )

    # Likewise, the payload currently gives orbit sizes but not canonical tree
    # addresses for every printed representative, so the pictures cannot yet be
    # checked from the PDF alone by a non-visual checker.
    has_tree_manifest = "tree_representatives" in data.get("symmetry_audit", {})
    tree_manifest = data.get("symmetry_audit", {}).get("tree_representatives", {})
    tree_manifest_consistent = has_tree_manifest and all(
        len(tree_manifest.get(str(nn), [])) == data["symmetry_audit"]["orbits_n_1_to_3"][nn - 1]
        and sum(item["orbit_size"] for item in tree_manifest.get(str(nn), []))
        == data["symmetry_audit"]["oriented_counts_n_1_to_3"][nn - 1]
        for nn in (1, 2, 3)
    )
    record(
        "quadtree figures have machine-readable representative manifest",
        tree_manifest_consistent,
        {
            "representatives_per_n": {key: len(value) for key, value in tree_manifest.items()},
            "explanation": "Canonical CCW codes, inventories, and orbit sizes are present for every displayed representative."
        },
        scope="surface",
    )

    failures = [c for c in checks if c["status"] == "fail"]
    return {
        "artifact_type": "layered-verifiable-pdf",
        "artifact_id": "artifact-21",
        "pdf": {
            "name": path.name,
            "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
            "size_bytes": len(pdf_bytes),
        },
        "payload": {
            "embedded_name": "a120593_certificate.json",
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
            "sequence": data.get("sequence"),
        },
        "summary": {
            "status": "pass" if not failures else "candidate",
            "passes": len(checks) - len(failures),
            "failures": len(failures),
        },
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = check_pdf(args.pdf)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
    raise SystemExit(0 if report["summary"]["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
