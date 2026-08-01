#!/usr/bin/env python3
"""One-case exact generalized polynomial-kernel pilot for A120592."""

from __future__ import annotations

import json
import resource
import time
from pathlib import Path

import sympy as sp

from expand_target_coverage import CORE
from guv_termwise_certificate_factory import build_case, expr_text
from relay_factory_v02 import add_semantic_objects, parse_expr

n, u = sp.symbols("n u")


def matrix(obj: dict) -> sp.Matrix:
    return sp.Matrix([[parse_expr(v) for v in row] for row in obj["entries"]])


def main() -> None:
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[1]
    case_id = "A120592"
    q, r, b, _ = CORE[case_id]
    case_root = root / "examples" / case_id
    terms = json.loads((case_root / "data/terms.json").read_text())["terms"]
    D = 1 - 3 * u - 2 * u**2
    run = root / "runs" / "A120592-polynomial-pilot"
    blob = build_case(
        q,
        run,
        23,
        D_override=D,
        terms_override=terms,
        check_normalized_plaintext=False,
    )
    add_semantic_objects(blob)
    blob["format"] = "RELAY-CT-generalized-polynomial-pilot-v0.1"
    blob["case_id"] = case_id
    blob["objects"]["sequence_family"]["ordinary_generating_function"].update({
        "symbol": "A(x)",
        "algebraic_equation": "5*A(x)=4+4*x+A(x)^3",
    })
    blob["objects"]["integrand_family"].update({
        "formula": "2/(n*u^n*D(u)^n)",
        "rho_form": "2/(n*rho(u)^n)",
        "residue_relation": "a(n)=Res_{u=0} 2/(n*rho(u)^n) du",
    })

    objects = blob["objects"]
    mats = objects["matrices"]
    G, Gi = matrix(mats["G"]), matrix(mats["G_inverse"])
    E, U, V = matrix(mats["embedding_E"]), matrix(mats["U"]), matrix(mats["V"])
    J, Xfull, X = matrix(mats["J"]), matrix(mats["X_full"]), matrix(mats["X"])
    P = sp.Matrix([parse_expr(v) for v in objects["p_recurrence"]["coefficients"]])
    rho = parse_expr(objects["input_polynomials"]["rho_q"])
    N = parse_expr(objects["rational_certificate"]["numerator_N"])
    denominator_power = objects["rational_certificate"]["denominator_power"]

    checks = {}
    def check(name: str, condition: bool, detail: object = 0):
        checks[name] = {"pass": bool(condition), "detail": str(detail)}
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    check("D_override_exact", sp.expand(parse_expr(objects["input_polynomials"]["D_q"]) - D) == 0)
    check("rho_equals_uD", sp.expand(rho - u * D) == 0)
    check("G_inverse", (G * Gi - sp.eye(2 * q)).is_zero_matrix)
    check("GUV_split", (G * sp.Matrix.vstack(U, V) - E).is_zero_matrix)
    check("Xfull_last_row_zero", all(sp.cancel(Xfull[q - 1, c]) == 0 for c in range(q)))
    check("X_rank", X.to_DM(field=True).rank() == q - 1, X.to_DM(field=True).rank())
    check("X_nullity_one", len(X.nullspace()) == 1, len(X.nullspace()))
    check("X_times_P", (X * P).applyfunc(sp.cancel).is_zero_matrix)
    replayed = []
    for chain in objects["pole_lowering_chains"]:
        current = sp.Matrix([parse_expr(v) for v in chain["initial_vector"]])
        for step in chain["steps"]:
            encoded_input = sp.Matrix([parse_expr(v) for v in step["input_vector"]])
            encoded_v = sp.Matrix([parse_expr(v) for v in step["certificate_vector_Vw"]])
            encoded_output = sp.Matrix([parse_expr(v) for v in step["output_vector_Tm_w"]])
            pole = parse_expr(step["pole_parameter"])
            check(
                f"lower_shift_{chain['shift']}_step_{step['lowering_index']}_input",
                (current - encoded_input).applyfunc(sp.cancel).is_zero_matrix,
            )
            computed_v = (V * current).applyfunc(sp.cancel)
            check(
                f"lower_shift_{chain['shift']}_step_{step['lowering_index']}_V",
                (computed_v - encoded_v).applyfunc(sp.cancel).is_zero_matrix,
            )
            current = (U * current - J * computed_v / pole).applyfunc(sp.cancel)
            check(
                f"lower_shift_{chain['shift']}_step_{step['lowering_index']}_output",
                (current - encoded_output).applyfunc(sp.cancel).is_zero_matrix,
            )
        scale = parse_expr(chain["shift_ratio_scale"])
        replayed.append((scale * current).applyfunc(sp.cancel))
    check("all_lowered_columns_rebuild_Xfull", (sp.Matrix.hstack(*replayed) - Xfull).applyfunc(sp.cancel).is_zero_matrix)
    term_residuals = [
        sum(int(P[j].subs(n, k)) * terms[k + j] for j in range(q))
        for k in range(1, len(terms) - q + 1)
    ]
    check("published_terms_recurrence", all(v == 0 for v in term_residuals), max(map(abs, term_residuals), default=0))
    scales = [sp.cancel(P[j] * n / (n + j)) for j in range(q)]
    check("recurrence_scales_polynomial", all(sp.denom(v) == 1 for v in scales))
    rp = sp.Poly(rho, n, u, domain=sp.QQ)
    np = sp.Poly(N, n, u, domain=sp.QQ)
    residual = rp * np.diff(u) - sp.Poly(n + q - 2, n, u, domain=sp.QQ) * sp.Poly(sp.diff(rho, u), n, u, domain=sp.QQ) * np
    for j, scale in enumerate(scales):
        residual -= sp.Poly(scale, n, u, domain=sp.QQ) * rp ** (q - 1 - j)
    check("cleared_telescoping_identity", residual.is_zero)
    ode = objects["ode_from_recurrence"]
    check("ode_series_residual", ode["verification"]["series_residual"]["pass"])
    check("ode_recurrence_correspondence", ode["verification"]["recurrence_coefficient_correspondence"]["pass"])

    stats = {
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "G_shape": list(G.shape),
        "G_nonzero": sum(v != 0 for v in G),
        "G_determinant": str(G.det()),
        "X_shape": list(X.shape),
        "X_rank": int(X.to_DM(field=True).rank()),
        "recurrence_order": q - 1,
        "recurrence_degree": max(int(sp.degree(v, n)) for v in P),
        "certificate_denominator_power": denominator_power,
        "certificate_degree_n": int(sp.degree(N, n)),
        "certificate_degree_u": int(sp.degree(N, u)),
    }
    blob["pilot_checks"] = checks
    blob["pilot_statistics"] = stats
    (run / "case.json").write_text(json.dumps(blob, indent=2, sort_keys=True) + "\n")
    (run / "validation.json").write_text(json.dumps({
        "status": "verified",
        "passed_checks": sum(v["pass"] for v in checks.values()),
        "total_checks": len(checks),
        "checks": checks,
        "statistics": stats,
    }, indent=2, sort_keys=True) + "\n")

    for name, source in {
        "matrices": "objects/matrices",
        "recurrence": "objects/p_recurrence",
        "certificate": "objects/rational_certificate",
        "ode": "objects/ode_from_recurrence",
    }.items():
        (case_root / "data" / f"{name}.json").write_text(json.dumps({
            "status": "verified",
            "canonical_source": "runs/A120592-polynomial-pilot/case.json#/" + source,
            "pilot_statistics": stats,
        }, indent=2, sort_keys=True) + "\n")
    manifest_path = case_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["case_state"] = "ANALYTIC_COMPLETE"
    for name in ("matrices", "recurrence", "certificate", "ode"):
        manifest["components"][name] = {
            "status": "verified",
            "canonical_path": f"data/{name}.json",
        }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case_id": case_id, "checks": len(checks), "statistics": stats}))


if __name__ == "__main__":
    main()
