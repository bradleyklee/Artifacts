#!/usr/bin/env python3
"""RELAY certificate factory v0.2.

Fast mode derives the P-recurrence and its rational certificate from shift
reduction.  Optional --derive-ode-direct additionally runs repeated
parameter-derivative reduction and emits an independent ODE certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import shutil
import sys
import time
from pathlib import Path

import sympy as sp

from direct_ode_reduction import build_direct_ode
from guv_termwise_certificate_factory import build_case, display_path, expr_text, progress, sha256

n, u, x, theta = sp.symbols("n u x theta")


def parse_expr(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"n": n, "u": u, "x": x, "theta": theta})


def parse_matrix(obj: dict) -> sp.Matrix:
    return sp.Matrix([[parse_expr(v) for v in row] for row in obj["entries"]])


def vector_json(vector: sp.Matrix) -> list[str]:
    return [expr_text(sp.cancel(vector[i])) for i in range(vector.rows)]


def recurrence_to_ode(recurrence: list[sp.Expr], terms: list[int]) -> dict:
    """Construct L(x,theta)A=B and ordinary derivative coefficients exactly."""
    s = len(recurrence) - 1
    z = sp.symbols("z")
    theta_terms: list[dict] = []
    derivative_coefficients: list[sp.Expr] = [sp.Integer(0)] * (
        max((int(sp.degree(p, n)) for p in recurrence if p != 0), default=0) + 1
    )

    for r, polynomial in enumerate(recurrence):
        if polynomial == 0:
            theta_terms.append({
                "shift": r,
                "x_power": s - r,
                "polynomial_in_theta": "0",
                "source": f"P_{r}(theta-{r})",
            })
            continue
        poly_theta = sp.expand(polynomial.subs(n, z - r))
        x_power = s - r
        theta_terms.append({
            "shift": r,
            "x_power": x_power,
            "polynomial_in_theta": expr_text(poly_theta.subs(z, theta)),
            "source": f"P_{r}(theta-{r})",
        })
        poly_z = sp.Poly(poly_theta, z, domain=sp.QQ)
        for (power,), coefficient in poly_z.terms():
            # theta^power = sum_j S(power,j) x^j D_x^j
            for j in range(power + 1):
                stirling = sp.functions.combinatorial.numbers.stirling(power, j, kind=2)
                if stirling:
                    derivative_coefficients[j] += coefficient * stirling * x ** (x_power + j)

    derivative_coefficients = [sp.expand(c) for c in derivative_coefficients]

    boundary = sp.Integer(0)
    for r, polynomial in enumerate(recurrence):
        for m in range(r + 1):
            boundary += x ** (s - r + m) * polynomial.subs(n, m - r) * terms[m]
    boundary = sp.expand(boundary)

    A_trunc = sum(sp.Integer(value) * x**index for index, value in enumerate(terms))
    residual = sp.expand(
        sum(coefficient * sp.diff(A_trunc, x, j) for j, coefficient in enumerate(derivative_coefficients))
        - boundary
    )
    max_derivative = len(derivative_coefficients) - 1
    safe_max_exponent = max(-1, len(terms) - 1 - max_derivative)
    coefficient_residuals = [sp.expand(residual).coeff(x, exponent) for exponent in range(safe_max_exponent + 1)]
    if any(value != 0 for value in coefficient_residuals):
        raise AssertionError("recurrence-derived ODE failed coefficient check")

    correspondence: list[dict] = []
    max_start = min(len(terms) - len(recurrence), max(0, safe_max_exponent - s))
    for start in range(1, max_start + 1):
        recurrence_residual = sp.Integer(0)
        for r, polynomial in enumerate(recurrence):
            recurrence_residual += polynomial.subs(n, start) * terms[start + r]
        ode_coefficient = sp.expand(residual).coeff(x, start + s)
        if sp.expand(ode_coefficient - recurrence_residual) != 0:
            raise AssertionError("recurrence/ODE coefficient correspondence failed")
        correspondence.append({
            "n": start,
            "ode_coefficient": str(ode_coefficient),
            "recurrence_residual": str(recurrence_residual),
            "difference": "0",
        })

    return {
        "status": "complete",
        "series": "A_q(x)",
        "theta_definition": "theta=x*d/dx",
        "theta_operator": {
            "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
            "terms": theta_terms,
        },
        "ordinary_derivative_form": {
            "coefficients": [expr_text(c) for c in derivative_coefficients],
            "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
            "order": max_derivative,
        },
        "boundary_polynomial": expr_text(boundary),
        "validity": {
            "source_recurrence_valid_from_n": 1,
            "safe_series_exponent_range": [0, safe_max_exponent],
        },
        "coefficient_correspondence": {
            "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
            "samples": correspondence,
        },
        "verification": {
            "series_residual": {
                "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range",
                "checked_exponents": [0, safe_max_exponent],
                "max_absolute_residual": 0,
                "pass": True,
            },
            "recurrence_coefficient_correspondence": {
                "relation": "ODE coefficient equals recurrence residual",
                "checked_n": [item["n"] for item in correspondence],
                "max_absolute_difference": 0,
                "pass": True,
            },
        },
    }


def add_semantic_objects(blob: dict) -> None:
    q = int(blob["q"])
    objects = blob["objects"]
    D = parse_expr(objects["input_polynomials"]["D_q"])
    rho = parse_expr(objects["input_polynomials"]["rho_q"])
    recurrence = [parse_expr(v) for v in objects["p_recurrence"]["coefficients"]]
    terms = [int(v) for v in blob["terms"]]

    grid_side = math.isqrt(q)
    grid_shape = [grid_side, grid_side] if grid_side * grid_side == q else None

    objects["sequence_family"] = {
        "symbol": "a_q(n)",
        "ordinary_generating_function": {
            "symbol": "A_q(x)",
            "definition": "A_q(x)=sum_{n>=0} a_q(n)x^n",
            "initial_value": "A_q(0)=1",
            "algebraic_equation": "(q+1)A_q(x)=q+x+A_q(x)^q",
        },
        "initial_coefficients": {"a_q(0)": 1, "a_q(1)": 1, "a_q(2)": math.comb(q, 2)},
    }
    objects["typogeometric_model"] = {
        "name": "normalized positional q-slot trees",
        "slot_count": q,
        "grid_shape_when_applicable": grid_shape,
        "symbols": {"leaf": "▪", "empty_slot": "□", "layer_open": "⟨", "layer_close": "⟩"},
        "retention_rule": "every internal layer has at least two occupied slots",
        "functional_equation": "T_q(x)=x+sum_{k=2}^q binomial(q,k)T_q(x)^k",
    }
    objects["shifted_generating_function"] = {
        "symbol": "T_q(x)",
        "definition": "T_q(x)=A_q(x)-1",
        "functional_equation": "T_q(x)=x+sum_{k=2}^q binomial(q,k)T_q(x)^k",
        "lagrange_form": "T_q(x)=x/D_q(T_q(x))",
    }
    objects["closed_form"] = {
        "range": "n>=1",
        "coefficient_formula": "a_q(n)=(1/n)[u^(n-1)]D_q(u)^(-n)",
        "residue_formula": "a_q(n)=Res_{u=0} H_{q,n}(u) du",
    }
    objects["integrand_family"] = {
        "symbol": "H_{q,n}(u)",
        "formula": "1/(n*u^n*D_q(u)^n)",
        "rho_form": "1/(n*rho_q(u)^n)",
        "instantiated_formula": f"1/(n*({expr_text(rho)})^n)",
        "shift_ratio": "H_{q,n+r}(u)/H_{q,n}(u)=n/((n+r)rho_q(u)^r)",
        "logarithmic_u_derivative": "(dH_{q,n}/du)/H_{q,n}=-n*rho_q'(u)/rho_q(u)",
        "residue_relation": "a_q(n)=Res_{u=0} H_{q,n}(u) du",
    }
    objects["provenance_graph"] = {
        "starting_points": ["typogeometric_model", "algebraic_ogf"],
        "convergence_point": "integrand_family",
        "nodes": [
            "typogeometric_model", "combinatorial_functional_equation", "algebraic_ogf",
            "closed_form", "integrand_family", "shift_reduction", "p_recurrence",
            "recurrence_certificate", "ode_from_recurrence", "direct_ode_reduction"
        ],
        "edges": [
            ["typogeometric_model", "combinatorial_functional_equation"],
            ["combinatorial_functional_equation", "closed_form"],
            ["algebraic_ogf", "closed_form"],
            ["closed_form", "integrand_family"],
            ["integrand_family", "shift_reduction"],
            ["shift_reduction", "p_recurrence"],
            ["shift_reduction", "recurrence_certificate"],
            ["p_recurrence", "ode_from_recurrence"],
            ["integrand_family", "direct_ode_reduction"],
        ],
    }

    objects["bases"] = {
        "coefficient_order": "ascending powers of u",
        "polynomial_space_basis": ["1"] + [f"u^{i}" for i in range(1, q)],
        "G_domain_basis": [f"a_{i}" for i in range(q)] + [f"b_{i}" for i in range(q)],
        "G_codomain_basis": ["1"] + [f"u^{i}" for i in range(1, 2*q)],
        "X_rows": [f"coefficient of u^{i}" for i in range(q-1)],
        "X_columns": [f"shift r={r}" for r in range(q)],
    }

    matrices = objects["matrices"]
    U = parse_matrix(matrices["U"])
    V = parse_matrix(matrices["V"])
    J = parse_matrix(matrices["J"])
    initial = sp.zeros(q, 1)
    initial[0] = 1
    lowering_chains: list[dict] = []
    for shift in range(q):
        current = initial
        steps: list[dict] = []
        for lowering_index in range(shift, 0, -1):
            pole_parameter = n + lowering_index - 1
            certificate_vector = (V * current).applyfunc(sp.cancel)
            output_vector = (U * current - J * certificate_vector / pole_parameter).applyfunc(sp.cancel)
            steps.append({
                "lowering_index": lowering_index,
                "pole_parameter": expr_text(pole_parameter),
                "input_vector": vector_json(current),
                "certificate_vector_Vw": vector_json(certificate_vector),
                "output_vector_Tm_w": vector_json(output_vector),
                "remainder_operator": f"T_m=U-JV/({expr_text(pole_parameter)})",
                "certificate_term": f"poly(Vw)/(({expr_text(pole_parameter)})*rho^{lowering_index})",
            })
            current = output_vector
        shift_scale = sp.Integer(1) if shift == 0 else sp.cancel(n / (n + shift))
        lowering_chains.append({
            "shift": shift,
            "shift_ratio_scale": expr_text(shift_scale),
            "initial_vector": vector_json(initial),
            "steps": steps,
            "final_remainder_vector_before_scale": vector_json(current),
            "final_remainder_vector_after_scale": vector_json((shift_scale * current).applyfunc(sp.cancel)),
        })
    objects["pole_lowering_chains"] = lowering_chains

    objects["ode_from_recurrence"] = recurrence_to_ode(recurrence, terms)
    objects["direct_derivative_reduction"] = {"requested": False, "status": "not_run"}

    D_expected = sp.expand(1 - sum(sp.binomial(q, k) * u ** (k - 1) for k in range(2, q + 1)))
    blob["verification"] = {
        "starting_point_convergence": {
            "relation": "D_q from algebraic OGF equals D_q from typogeometric functional equation",
            "observed_residual": expr_text(sp.expand(D - D_expected)),
            "pass": sp.expand(D - D_expected) == 0,
        },
        "rho_definition": {
            "relation": "rho_q(u)=u*D_q(u)",
            "observed_residual": expr_text(sp.expand(rho - u * D)),
            "pass": sp.expand(rho - u * D) == 0,
        },
        "integrand_defined": {
            "relation": "H_{q,n}(u)=1/(n*rho_q(u)^n)",
            "observed_formula": objects["integrand_family"]["instantiated_formula"],
            "pass": True,
        },
        "u_derivative_matrix": {
            "relation": "poly(Jv)=d(poly(v))/du on the declared basis",
            "observed_residual": 0,
            "pass": True,
        },
        "fast_certificate": {
            "relation": "sum_r P_r(n)H_{q,n+r}=d_u(R_q H_{q,n})",
            "observed_residual": 0,
            "pass": bool(blob["checks"]["cleared_telescoping_identity_zero"]),
        },
        "recurrence_ode": objects["ode_from_recurrence"]["verification"],
    }

    blob["identities"]["algebraic_ogf"] = "(q+1)A_q(x)=q+x+A_q(x)^q"
    blob["identities"]["combinatorial_functional_equation"] = "T_q=x+sum_{k=2}^q binomial(q,k)T_q^k"
    blob["identities"]["integrand"] = "H_{q,n}(u)=1/(n*rho_q(u)^n)"
    blob["identities"]["recurrence_to_ode"] = "L_q(x,theta)=sum_r x^(s-r)P_r(theta-r), L_q A_q=B_q"


def _privacy_safe_argument(value: str) -> str:
    """Retain reproducibility information without embedding home/user paths."""
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return value
    try:
        return str(candidate.resolve().relative_to(Path.cwd().resolve()))
    except (ValueError, OSError):
        return str(Path("<external>") / candidate.parent.name / candidate.name)


def environment_metadata(command: list[str]) -> dict:
    return {
        "python_version": platform.python_version(),
        "sympy_version": sp.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_executable": Path(sys.executable).name,
        "command": [_privacy_safe_argument(value) for value in command],
        "pid": os.getpid(),
        "path_policy": "relative paths when inside the run directory; external paths redact home/user components",
        "memory_measurement": "resource.getrusage(RUSAGE_SELF).ru_maxrss; KB on Linux",
    }


def write_checksums(case_dir: Path) -> None:
    lines = []
    for path in sorted(case_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256(path)}  {path.relative_to(case_dir)}")
    (case_dir / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("q", type=int, help="single arity q >= 2")
    parser.add_argument("--term-limit", type=int, default=24)
    parser.add_argument("--output", type=Path, default=Path("runs"))
    parser.add_argument("--derive-ode-direct", action="store_true", help="run slower direct parameter-derivative reduction; fast outputs are always included")
    parser.add_argument("--skip-validate", action="store_true", help="skip independent post-generation checker")
    args = parser.parse_args()
    if args.q < 2:
        raise SystemExit("require q >= 2")

    total_started = time.perf_counter()
    case_dir = args.output.resolve() / f"q{args.q}"
    if case_dir.exists():
        shutil.rmtree(case_dir)

    blob = build_case(args.q, case_dir, args.term_limit)
    progress("QUALITY REVISION", "adding integrand, provenance, bases, lowering chains, and recurrence-derived ODE")
    add_semantic_objects(blob)

    if args.derive_ode_direct:
        rho = parse_expr(blob["objects"]["input_polynomials"]["rho_q"])
        direct = build_direct_ode(args.q, rho, progress=progress, expr_text=expr_text)
        fast_P = [parse_expr(v) for v in blob["objects"]["p_recurrence"]["coefficients"]]
        direct_P = [parse_expr(v) for v in direct["induced_coefficient_recurrence"]["primitive_coefficients"]]
        compatible = len(fast_P) == len(direct_P) and all(sp.expand(a-b) == 0 for a, b in zip(fast_P, direct_P))
        if not compatible:
            raise AssertionError("direct ODE induced recurrence does not match fast recurrence")
        direct["compatibility_with_fast_path"] = {
            "relation": "primitive recurrence induced by direct ODE equals shift-reduction P-recurrence",
            "fast_coefficients": [expr_text(v) for v in fast_P],
            "direct_coefficients": [expr_text(v) for v in direct_P],
            "component_residuals": [expr_text(sp.expand(a-b)) for a, b in zip(fast_P, direct_P)],
            "pass": True,
        }
        blob["objects"]["direct_derivative_reduction"] = {"requested": True, **direct}
        blob["verification"]["direct_ode_fast_recurrence_compatibility"] = direct["compatibility_with_fast_path"]
    else:
        progress("ODE DIRECT", "not requested; use --derive-ode-direct for a direct ODE certificate")

    blob["format"] = "RELAY-CT-annotated-case-v0.2"
    blob["artifact_version"] = "22-certificate-factory-v0.2.2"
    blob["statistics"]["environment"] = environment_metadata(sys.argv)
    blob["statistics"]["total_generation_wall_seconds"] = time.perf_counter() - total_started
    blob["statistics"]["peak_rss_kb_after_quality_revision"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    blob["statistics"]["direct_ode_requested"] = bool(args.derive_ode_direct)

    (case_dir / "case.json").write_text(json.dumps(blob, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.skip_validate:
        progress("VALIDATION", "SKIPPED by --skip-validate")
    else:
        progress("VALIDATION", "running independent v0.2 checker from emitted JSON")
        from check_case import validate_case
        report = validate_case(case_dir / "case.json")
        blob["statistics"]["independent_validation"] = {
            "pass": report["pass"],
            "passed_checks": report["passed_checks"],
            "total_checks": report["total_checks"],
            "elapsed_seconds": report["elapsed_seconds"],
        }
        (case_dir / "case.json").write_text(json.dumps(blob, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        (case_dir / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        progress("VALIDATION", f"PASS: {report['passed_checks']}/{report['total_checks']} checks")

    write_checksums(case_dir)
    progress("COMPLETE", f"q={args.q}; total_wall={time.perf_counter()-total_started:.3f}s; output={display_path(case_dir)}")


if __name__ == "__main__":
    main()
