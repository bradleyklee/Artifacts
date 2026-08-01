#!/usr/bin/env python3
"""Exact direct-x reduction pilot for rational descendant A244594."""

from __future__ import annotations

import json
import argparse
import resource
import time
from pathlib import Path

import sympy as sp

from direct_ode_reduction import build_direct_ode
from guv_termwise_certificate_factory import expr_text, progress
from relay_factory_v02 import recurrence_to_ode
from expand_target_coverage import DESC

n, u, x = sp.symbols("n u x")


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"n": n, "u": u, "x": x})


def matrix(obj: dict) -> sp.Matrix:
    return sp.Matrix([[parse(v) for v in row] for row in obj["entries"]])


def ode_for_A_prime_to_recurrence(coefficients: list[sp.Expr]) -> list[sp.Expr]:
    """Extract a recurrence without the normalized q3 degree assumption."""
    by_shift: dict[int, sp.Expr] = {}
    for derivative_order, coefficient in enumerate(coefficients):
        for (power,), scalar in sp.Poly(coefficient, x, domain=sp.QQ).terms():
            shift = derivative_order + 1 - power
            source = n + shift
            factor = sp.prod(source - j for j in range(derivative_order + 1))
            by_shift[shift] = by_shift.get(shift, 0) + scalar * factor
    minimum = min(by_shift)
    if minimum < 0:
        # Move the coefficient index forward so the first shift is zero.
        by_shift = {shift - minimum: value.subs(n, n - minimum) for shift, value in by_shift.items()}
    maximum = max(by_shift)
    raw = [sp.factor(by_shift.get(shift, 0)) for shift in range(maximum + 1)]
    # Primitive integer-polynomial normalization.
    common = 0
    for value in raw:
        common = sp.gcd(common, value)
    raw = [sp.cancel(value / common) for value in raw]
    return raw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id", nargs="?", default="A244594")
    args = parser.parse_args()
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[1]
    case_id = args.case_id
    if case_id not in DESC:
        raise SystemExit("require one of the verified rational descendants")
    case_root = root / "examples" / case_id
    terms = json.loads((case_root / "data/terms.json").read_text())["terms"]
    q, r, s, _ = DESC[case_id]
    d = sp.Rational(s, r-q)
    coefficients = {k: sp.binomial(q,k)*d**k/s for k in range(2,q+1)}
    h = 1 + d*u
    p = sp.expand(u*(1-sum(coefficients[k]*u**(k-1) for k in coefficients)))
    g = sp.expand(p - x * h)
    result = build_direct_ode(
        q,
        p,
        progress=progress,
        expr_text=expr_text,
        numerator_seed=h,
        denominator_g=g,
    )
    mats = result["matrices"]
    G, Gi = matrix(mats["Gx"]), matrix(mats["Gx_inverse"])
    U, V, J = matrix(mats["Ux"]), matrix(mats["Vx"]), matrix(mats["J"])

    # Correct rational-rho derivatives:
    # D_x^j(h/g)=j!*h^(j+1)/g^(j+1).  Polynomial division by g can
    # create several pole components before Hermite lowering.
    reduced_columns = []
    derivative_audits = []
    derivative_certificates = []
    for derivative_order in range(q):
        components = {derivative_order + 1: sp.factorial(derivative_order) * h ** (derivative_order + 1)}
        normalized: dict[int, sp.Expr] = {}
        while components:
            pole, numerator = components.popitem()
            quotient, remainder = sp.div(numerator, g, u)
            normalized[pole] = sp.expand(normalized.get(pole, 0) + remainder)
            if quotient != 0 and pole > 1:
                components[pole - 1] = sp.expand(components.get(pole - 1, 0) + quotient)
            # A pole-zero polynomial has zero contour residue and is discarded.
        final = sp.zeros(q, 1)
        cert = sp.Integer(0)
        audit = []
        for pole, numerator in sorted(normalized.items(), reverse=True):
            current = sp.Matrix([sp.expand(numerator).coeff(u, degree) for degree in range(q)])
            for k in range(pole - 1, 0, -1):
                cv = (V * current).applyfunc(sp.cancel)
                output = (U * current - J * cv / k).applyfunc(sp.cancel)
                cert += sum(cv[i] * u**i for i in range(q)) * g ** (q - 1 - k) / k
                audit.append({
                    "pole_parameter": k,
                    "input": [expr_text(v) for v in current],
                    "V": [expr_text(v) for v in cv],
                    "output": [expr_text(v) for v in output],
                })
                current = output
            final += current
        reduced_columns.append(final.applyfunc(sp.cancel))
        derivative_certificates.append(sp.cancel(cert))
        derivative_audits.append({
            "derivative_order": derivative_order,
            "initial_numerator": expr_text(sp.factorial(derivative_order) * h ** (derivative_order + 1)),
            "normalized_pole_numerators": {str(k): expr_text(v) for k, v in normalized.items()},
            "steps": audit,
            "final_remainder": [expr_text(v) for v in final],
        })
    Xfull = sp.Matrix.hstack(*reduced_columns)
    X = Xfull[:q-1, :]
    null = X.to_DM(field=True).nullspace().to_Matrix()
    if X.to_DM(field=True).rank() != q-1 or null.shape != (1, q):
        raise AssertionError("corrected descendant derivative matrix has unexpected rank/nullity")
    from direct_ode_reduction import _primitive_vector
    Cvec = _primitive_vector(list(null[0, :]), x)
    C = list(Cvec)
    certificate_numerator = sp.cancel(sum(C[j] * derivative_certificates[j] for j in range(q)))
    if sp.denom(certificate_numerator) != 1:
        raise AssertionError("corrected descendant certificate numerator is not polynomial")
    left = sum(C[j] * sp.factorial(j) * h ** (j + 1) * g ** (q-j-1) for j in range(q))
    right = sp.expand(g * sp.diff(certificate_numerator, u) - (q-1) * sp.diff(g, u) * certificate_numerator)
    corrected_identity_residual = sp.Poly(sp.together(left-right),x,u,domain=sp.QQ)
    if not corrected_identity_residual.is_zero:
        raise AssertionError("corrected descendant integrand identity failed")

    old_P = [parse(v) for v in result["induced_coefficient_recurrence"]["primitive_coefficients"]]
    P = ode_for_A_prime_to_recurrence(C)
    ode_A = recurrence_to_ode(P, terms)

    checks = {}
    def check(name: str, condition: bool, detail: object = 0):
        checks[name] = {"pass": bool(condition), "detail": str(detail)}
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    check("Gx_invertible", result["verification"]["Gx_invertible"]["pass"])
    check("Gx_Ux_Vx_split", result["verification"]["Gx_Ux_Vx_split"]["pass"])
    check("corrected_integrand_certificate", corrected_identity_residual.is_zero)
    check("Gx_inverse_replayed", (G * Gi - sp.eye(2 * q)).applyfunc(sp.cancel).is_zero_matrix)
    check("X_rank_nullity", X.to_DM(field=True).rank() == q-1 and len(X.nullspace()) == 1)
    term_residuals = [
        sum(int(P[j].subs(n, k)) * terms[k+j] for j in range(len(P)))
        for k in range(1, len(terms)-len(P)+1)
    ]
    check("published_terms_recurrence", all(v == 0 for v in term_residuals), max(map(abs, term_residuals), default=0))
    old_term_residuals = [
        sum(int(old_P[j].subs(n, k)) * terms[k+j] for j in range(len(old_P)))
        for k in range(1, len(terms)-len(old_P)+1)
    ]
    check("normalized_q3_translator_detected_inapplicable", any(v != 0 for v in old_term_residuals))
    check("recurrence_ode_series", ode_A["verification"]["series_residual"]["pass"])
    check("recurrence_ode_correspondence", ode_A["verification"]["recurrence_coefficient_correspondence"]["pass"])

    stats = {
        "wall_seconds": time.perf_counter()-started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "Gx_shape": list(G.shape),
        "Gx_nonzero": sum(v != 0 for v in G),
        "Gx_determinant": result["Gx"]["determinant"],
        "X_shape": list(X.shape),
        "X_rank": int(X.to_DM(field=True).rank()),
        "ode_for_A_prime_order": len(C)-1,
        "recurrence_order": len(P)-1,
        "certificate_degree_x": int(sp.degree(certificate_numerator, x)),
        "certificate_degree_u": int(sp.degree(certificate_numerator, u)),
    }
    payload = {
        "format": "RELAY-CT-rational-descendant-direct-x-pilot-v0.1",
        "case_id": case_id,
        "input": {
            "h": expr_text(h),
            "p": expr_text(p),
            "g": expr_text(g),
            "Phi": f"({expr_text(h)})/({expr_text(g)})",
        },
        "direct_reduction_base_matrices": {
            "matrices": result["matrices"],
            "Gx": result["Gx"],
            "bases": result["bases"],
            "note": "Only the denominator-based matrices are reused. Fixed-seed derivative columns from the generic helper are not valid for rational rho and are intentionally omitted.",
        },
        "corrected_numerator_aware_reduction": {
            "derivatives": derivative_audits,
            "X_full": [[expr_text(sp.cancel(Xfull[i,j])) for j in range(Xfull.cols)] for i in range(Xfull.rows)],
            "X": [[expr_text(sp.cancel(X[i,j])) for j in range(X.cols)] for i in range(X.rows)],
            "ode_for_A_prime": [expr_text(v) for v in C],
            "certificate": {
                "numerator": expr_text(certificate_numerator),
                "denominator_base": expr_text(g),
                "denominator_power": q-1,
            },
        },
        "recurrence": [expr_text(v) for v in P],
        "discarded_normalized_q3_recurrence": {
            "coefficients": [expr_text(v) for v in old_P],
            "reason": "translator dropped the backward shift caused by the cubic x coefficient",
            "first_residual": next(str(v) for v in old_term_residuals if v != 0),
        },
        "ode_for_A": ode_A,
        "checks": checks,
        "statistics": stats,
    }
    run = root / "runs" / f"{case_id}-direct-x-pilot"
    run.mkdir(parents=True, exist_ok=True)
    (run / "case.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (run / "validation.json").write_text(json.dumps({
        "status": "verified",
        "passed_checks": sum(v["pass"] for v in checks.values()),
        "total_checks": len(checks),
        "checks": checks,
        "statistics": stats,
    }, indent=2, sort_keys=True) + "\n")
    for name, source in {
        "matrices": "direct_reduction_base_matrices/matrices",
        "recurrence": "recurrence",
        "certificate": "corrected_numerator_aware_reduction/certificate",
        "ode": "ode_for_A",
    }.items():
        (case_root / "data" / f"{name}.json").write_text(json.dumps({
            "status": "verified",
            "canonical_source": f"runs/{case_id}-direct-x-pilot/case.json#/{source}",
            "pilot_statistics": stats,
        }, indent=2, sort_keys=True) + "\n")
    manifest_path = case_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["case_state"] = "ANALYTIC_COMPLETE"
    for name in ("matrices", "recurrence", "certificate", "ode"):
        manifest["components"][name] = {"status": "verified", "canonical_path": f"data/{name}.json"}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case_id": case_id, "checks": len(checks), "recurrence": [expr_text(v) for v in P], "ode_A_prime": [expr_text(v) for v in C], "statistics": stats}))


if __name__ == "__main__":
    main()
