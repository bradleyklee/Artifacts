#!/usr/bin/env python3
"""Independent exact checker for a RELAY-CT v0.2 annotated case.json."""
from __future__ import annotations

import argparse
import json
import math
import time

from progress_output import emit_progress
from pathlib import Path

import sympy as sp

n, u, x, theta, z = sp.symbols("n u x theta z")


def say(stage: str, message: str) -> None:
    emit_progress(f"CHECK {stage}", message)


def parse_expr(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"n": n, "u": u, "x": x, "theta": theta})


def parse_matrix(obj: dict) -> sp.Matrix:
    matrix = sp.Matrix([[parse_expr(value) for value in row] for row in obj["entries"]])
    if list(matrix.shape) != obj["shape"]:
        raise AssertionError(f"shape mismatch: encoded={obj['shape']} actual={matrix.shape}")
    return matrix


def parse_vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([parse_expr(value) for value in values])



def matrix_equal(left: sp.Matrix, right: sp.Matrix) -> bool:
    return left.shape == right.shape and (left - right).applyfunc(sp.cancel).is_zero_matrix


def primitive_vector(values: list[sp.Expr], variable: sp.Symbol) -> sp.Matrix:
    expressions = [sp.cancel(value) for value in values]
    denominators = [sp.Poly(sp.denom(value), variable, domain=sp.QQ) for value in expressions]
    common_denominator = denominators[0]
    for denominator in denominators[1:]:
        common_denominator = sp.lcm(common_denominator, denominator)
    polynomials = [sp.Poly(sp.cancel(v * common_denominator.as_expr()), variable, domain=sp.QQ) for v in expressions]
    common_polynomial = polynomials[0]
    for polynomial in polynomials[1:]:
        common_polynomial = sp.gcd(common_polynomial, polynomial)
    polynomials = [sp.exquo(polynomial, common_polynomial) for polynomial in polynomials]
    coefficient_lcm = 1
    for polynomial in polynomials:
        for coefficient in polynomial.all_coeffs():
            coefficient_lcm = sp.ilcm(coefficient_lcm, int(sp.denom(coefficient)))
    polynomials = [sp.Poly(sp.expand(p.as_expr() * coefficient_lcm), variable, domain=sp.ZZ) for p in polynomials]
    content = 0
    for polynomial in polynomials:
        content = math.gcd(content, abs(int(polynomial.content())))
    if content > 1:
        polynomials = [sp.Poly(p.as_expr() / content, variable, domain=sp.ZZ) for p in polynomials]
    if polynomials[-1].LC() < 0:
        polynomials = [-p for p in polynomials]
    return sp.Matrix([p.as_expr() for p in polynomials])


def recurrence_to_ode(recurrence: list[sp.Expr], terms: list[int]) -> tuple[list[sp.Expr], sp.Expr]:
    s = len(recurrence) - 1
    max_degree = max(int(sp.degree(p, n)) for p in recurrence)
    derivative_coefficients = [sp.Integer(0)] * (max_degree + 1)
    for r, polynomial in enumerate(recurrence):
        poly_theta = sp.Poly(sp.expand(polynomial.subs(n, z - r)), z, domain=sp.QQ)
        x_power = s - r
        for (power,), coefficient in poly_theta.terms():
            for j in range(power + 1):
                stirling = sp.functions.combinatorial.numbers.stirling(power, j, kind=2)
                derivative_coefficients[j] += coefficient * stirling * x ** (x_power + j)
    derivative_coefficients = [sp.expand(value) for value in derivative_coefficients]
    boundary = sp.Integer(0)
    for r, polynomial in enumerate(recurrence):
        for m in range(r + 1):
            boundary += x ** (s - r + m) * polynomial.subs(n, m - r) * terms[m]
    return derivative_coefficients, sp.expand(boundary)


def ode_prime_to_recurrence(ode_coefficients: list[sp.Expr]) -> list[sp.Expr]:
    order = len(ode_coefficients) - 1
    result = [sp.Integer(0) for _ in range(order + 1)]
    k = n - 1
    for derivative_order, coefficient_polynomial in enumerate(ode_coefficients):
        polynomial = sp.Poly(coefficient_polynomial, x, domain=sp.QQ)
        for (x_power,), scalar in polynomial.terms():
            shift = derivative_order - x_power
            if not 0 <= shift <= order:
                continue
            source_index = sp.expand(k - x_power + derivative_order)
            derivative_factor = sp.prod(source_index - h for h in range(derivative_order)) if derivative_order else 1
            result[shift] += scalar * derivative_factor * (source_index + 1)
    return [sp.factor(value) for value in result]


def validate_case(json_path: Path) -> dict:
    started = time.perf_counter()
    blob = json.loads(json_path.read_text(encoding="utf-8"))
    q = int(blob["q"])
    objects = blob["objects"]
    matrices = objects["matrices"]
    checks: dict[str, dict] = {}

    def record(name: str, passed: bool, value) -> None:
        checks[name] = {"pass": bool(passed), "value": value}
        if not passed:
            raise AssertionError(f"{name} failed: {value}")

    say("SCHEMA", f"q={q}; reading v0.2 labeled objects")
    record("format_v0_2", blob.get("format") == "RELAY-CT-annotated-case-v0.2", blob.get("format"))
    required_objects = {
        "input_polynomials", "matrices", "p_recurrence", "rational_certificate",
        "sequence_family", "typogeometric_model", "shifted_generating_function",
        "closed_form", "integrand_family", "provenance_graph", "bases",
        "pole_lowering_chains", "ode_from_recurrence", "direct_derivative_reduction",
    }
    record("required_primary_objects_present", required_objects <= set(objects), sorted(objects))

    say("SEMANTICS", "checking OGF, D, rho, integrand, and declared bases")
    D = parse_expr(objects["input_polynomials"]["D_q"])
    rho = parse_expr(objects["input_polynomials"]["rho_q"])
    expected_D = sp.expand(1 - sum(sp.binomial(q, k) * u ** (k - 1) for k in range(2, q + 1)))
    record("D_q_formula_exact", sp.expand(D - expected_D) == 0, sp.sstr(sp.expand(D - expected_D)))
    record("rho_equals_u_D", sp.expand(rho - u * D) == 0, sp.sstr(sp.expand(rho - u * D)))
    integrand = objects["integrand_family"]
    record("integrand_symbol_defined", integrand.get("symbol") == "H_{q,n}(u)", integrand.get("symbol"))
    record("integrand_rho_form_defined", integrand.get("rho_form") == "1/(n*rho_q(u)^n)", integrand.get("rho_form"))
    bases = objects["bases"]
    record("basis_order_explicit", bases.get("coefficient_order") == "ascending powers of u", bases.get("coefficient_order"))
    record("basis_dimension_q", len(bases["polynomial_space_basis"]) == q, len(bases["polynomial_space_basis"]))

    say("MATRICES", "parsing exact G, G_inverse, E, U, V, J, X")
    G = parse_matrix(matrices["G"])
    Ginv = parse_matrix(matrices["G_inverse"])
    E = parse_matrix(matrices["embedding_E"])
    U = parse_matrix(matrices["U"])
    V = parse_matrix(matrices["V"])
    J = parse_matrix(matrices["J"])
    Xfull = parse_matrix(matrices["X_full"])
    X = parse_matrix(matrices["X"])

    say("G", f"checking {G.rows}x{G.cols} determinant and inverse")
    det_g = sp.Integer(G.det())
    record("G_determinant_matches", det_g == int(blob["G"]["determinant"]), str(det_g))
    record("G_times_G_inverse_identity", (G * Ginv - sp.eye(2 * q)).is_zero_matrix, 0)
    record("GUV_split_exact", (G * sp.Matrix.vstack(U, V) - E).is_zero_matrix, 0)
    expected_J = sp.zeros(q, q)
    for col in range(1, q):
        expected_J[col - 1, col] = col
    record("J_derivative_matrix_exact", matrix_equal(J, expected_J), 0)

    say("LOWERING", "replaying every stored shift-reduction step")
    chains = objects["pole_lowering_chains"]
    record("lowering_chain_count", len(chains) == q, len(chains))
    rebuilt_columns = []
    for chain in chains:
        shift = int(chain["shift"])
        current = parse_vector(chain["initial_vector"])
        for step in chain["steps"]:
            pole_parameter = parse_expr(step["pole_parameter"])
            encoded_input = parse_vector(step["input_vector"])
            encoded_certificate = parse_vector(step["certificate_vector_Vw"])
            encoded_output = parse_vector(step["output_vector_Tm_w"])
            record(f"lowering_shift_{shift}_step_{step['lowering_index']}_input", matrix_equal(current, encoded_input), 0)
            computed_certificate = (V * current).applyfunc(sp.cancel)
            record(f"lowering_shift_{shift}_step_{step['lowering_index']}_V", matrix_equal(computed_certificate, encoded_certificate), 0)
            computed_output = (U * current - J * computed_certificate / pole_parameter).applyfunc(sp.cancel)
            record(f"lowering_shift_{shift}_step_{step['lowering_index']}_T", matrix_equal(computed_output, encoded_output), 0)
            current = computed_output
        scale = parse_expr(chain["shift_ratio_scale"])
        final_scaled = (scale * current).applyfunc(sp.cancel)
        record(f"lowering_shift_{shift}_final", matrix_equal(final_scaled, parse_vector(chain["final_remainder_vector_after_scale"])), 0)
        rebuilt_columns.append(final_scaled)
    rebuilt_Xfull = sp.Matrix.hstack(*rebuilt_columns)
    record("X_full_rebuilt_from_lowering", matrix_equal(rebuilt_Xfull, Xfull), 0)
    record("X_is_prefix_of_X_full", matrix_equal(X, Xfull[:q - 1, :]), 0)
    record("X_full_last_row_zero", all(sp.cancel(Xfull[q - 1, c]) == 0 for c in range(q)), 0)

    say("RECURRENCE", "checking exact kernel vector and rank")
    P = sp.Matrix([parse_expr(value) for value in objects["p_recurrence"]["coefficients"]])
    record("X_times_P_zero", (X * P).applyfunc(sp.cancel).is_zero_matrix, 0)
    rank_x = int(X.to_DM(field=True).rank())
    record("X_rank_q_minus_1", rank_x == q - 1, rank_x)

    say("CERTIFICATE", "checking cleared fast telescoping identity")
    N = parse_expr(objects["rational_certificate"]["numerator_N"])
    denominator_power = int(objects["rational_certificate"]["denominator_power"])
    record("certificate_denominator_power", denominator_power == q - 2, denominator_power)
    Npoly = sp.Poly(N, n, u, domain=sp.QQ)
    rhopoly = sp.Poly(rho, n, u, domain=sp.QQ)
    residual = rhopoly * Npoly.diff(u) - sp.Poly(n + q - 2, n, u, domain=sp.QQ) * sp.Poly(sp.diff(rho, u), n, u, domain=sp.QQ) * Npoly
    for r in range(q):
        scale = sp.cancel(P[r] * n / (n + r))
        record(f"recurrence_scale_{r}_polynomial", sp.denom(scale) == 1, str(scale))
        residual -= sp.Poly(scale, n, u, domain=sp.QQ) * rhopoly ** (q - 1 - r)
    record("cleared_telescoping_identity_zero", residual.is_zero, 0)

    terms = [int(value) for value in blob["terms"]]
    say("TERMS", "checking emitted terms against P-recurrence")
    term_residuals = []
    for start in range(1, len(terms) - q + 1):
        value = sum(int(P[r].subs(n, start)) * terms[start + r] for r in range(q))
        term_residuals.append(value)
    record("all_term_recurrence_residuals_zero", all(v == 0 for v in term_residuals), max(map(abs, term_residuals), default=0))

    say("RECURRENCE ODE", "rebuilding standard recurrence-to-ODE transform")
    stored_ode = objects["ode_from_recurrence"]
    expected_coefficients, expected_boundary = recurrence_to_ode(list(P), terms)
    stored_coefficients = [parse_expr(value) for value in stored_ode["ordinary_derivative_form"]["coefficients"]]
    stored_boundary = parse_expr(stored_ode["boundary_polynomial"])
    record("recurrence_ode_coefficients_exact", len(expected_coefficients) == len(stored_coefficients) and all(sp.expand(a-b) == 0 for a,b in zip(expected_coefficients, stored_coefficients)), 0)
    record("recurrence_ode_boundary_exact", sp.expand(expected_boundary - stored_boundary) == 0, sp.sstr(sp.expand(expected_boundary - stored_boundary)))
    A_trunc = sum(sp.Integer(value) * x**index for index, value in enumerate(terms))
    ode_residual = sp.expand(sum(c * sp.diff(A_trunc, x, j) for j, c in enumerate(stored_coefficients)) - stored_boundary)
    safe_max = len(terms) - 1 - (len(stored_coefficients) - 1)
    safe_values = [ode_residual.coeff(x, exponent) for exponent in range(max(0, safe_max + 1))]
    record("recurrence_ode_series_residual_zero", all(v == 0 for v in safe_values), max([abs(int(v)) for v in safe_values] or [0]))
    s = q - 1
    mapping_values = []
    for start in range(1, min(len(terms)-q+1, max(1, safe_max-s+1))):
        ode_value = ode_residual.coeff(x, start + s)
        rec_value = sum(P[r].subs(n, start) * terms[start+r] for r in range(q))
        mapping_values.append(sp.expand(ode_value - rec_value))
    record("recurrence_ode_coefficient_correspondence", all(v == 0 for v in mapping_values), 0)

    direct = objects["direct_derivative_reduction"]
    if direct.get("status") == "complete":
        say("DIRECT ODE", "checking direct parameter-derivative reduction and certificate")
        dm = direct["matrices"]
        Gx = parse_matrix(dm["Gx"])
        Gxinv = parse_matrix(dm["Gx_inverse"])
        Ex = parse_matrix(dm["embedding_E"])
        Ux = parse_matrix(dm["Ux"])
        Vx = parse_matrix(dm["Vx"])
        Jx = parse_matrix(dm["J"])
        Xofull = parse_matrix(dm["X_full"])
        Xo = parse_matrix(dm["X"])
        g = parse_expr(direct["integrand"]["denominator_g"])
        record("direct_g_equals_rho_minus_x", sp.expand(g - (rho-x)) == 0, sp.sstr(sp.expand(g-(rho-x))))
        det_gx = sp.factor(Gx.det())
        record("direct_Gx_determinant", sp.expand(det_gx - parse_expr(direct["Gx"]["determinant"])) == 0, sp.sstr(det_gx))
        record("direct_Gx_inverse", (Gx * Gxinv - sp.eye(2*q)).applyfunc(sp.cancel).is_zero_matrix, 0)
        record("direct_Gx_UV_split", (Gx * sp.Matrix.vstack(Ux, Vx) - Ex).applyfunc(sp.cancel).is_zero_matrix, 0)
        record("direct_J_exact", matrix_equal(Jx, expected_J), 0)

        rebuilt_direct_cols = []
        for derivative in direct["derivative_reductions"]:
            current = sp.zeros(q,1)
            current[0] = sp.factorial(int(derivative["derivative_order"]))
            for step in derivative["steps"]:
                m = int(step["pole_parameter"])
                encoded_input = parse_vector(step["input_vector"])
                encoded_certificate = parse_vector(step["certificate_vector"])
                encoded_output = parse_vector(step["output_vector"])
                record(f"direct_derivative_{derivative['derivative_order']}_m{m}_input", matrix_equal(current, encoded_input), 0)
                cert = (Vx * current).applyfunc(sp.cancel)
                record(f"direct_derivative_{derivative['derivative_order']}_m{m}_V", matrix_equal(cert, encoded_certificate), 0)
                out = (Ux * current - Jx * cert / m).applyfunc(sp.cancel)
                record(f"direct_derivative_{derivative['derivative_order']}_m{m}_T", matrix_equal(out, encoded_output), 0)
                current = out
            record(f"direct_derivative_{derivative['derivative_order']}_final", matrix_equal(current, parse_vector(derivative["final_remainder_vector"])), 0)
            rebuilt_direct_cols.append(current)
        rebuilt_Xofull = sp.Matrix.hstack(*rebuilt_direct_cols)
        record("direct_X_full_rebuilt", matrix_equal(rebuilt_Xofull, Xofull), 0)
        record("direct_X_prefix", matrix_equal(Xo, Xofull[:q-1,:]), 0)

        C = sp.Matrix([parse_expr(value) for value in direct["ode_for_A_prime"]["coefficients"]])
        record("direct_X_times_C_zero", (Xo*C).applyfunc(sp.cancel).is_zero_matrix, 0)
        record("direct_rank_q_minus_1", int(Xo.to_DM(field=True).rank()) == q-1, int(Xo.to_DM(field=True).rank()))
        record("direct_leading_ODE_coefficient_det", sp.expand(C[-1]-det_gx) == 0, sp.sstr(sp.expand(C[-1]-det_gx)))

        Node = parse_expr(direct["certificate"]["numerator"])
        left = sum(C[j] * sp.factorial(j) * g ** (q-j-1) for j in range(q))
        right = sp.expand(g*sp.diff(Node,u) - (q-1)*sp.diff(g,u)*Node)
        direct_residual = sp.Poly(sp.together(left-right),x,u,domain=sp.QQ)
        record("direct_ODE_certificate_identity_zero", direct_residual.is_zero, 0)

        raw_induced = ode_prime_to_recurrence(list(C))
        primitive_induced = primitive_vector(raw_induced, n)
        record("direct_ODE_induced_recurrence_equals_P", all(sp.expand(primitive_induced[i]-P[i]) == 0 for i in range(q)), 0)

        # Direct ODE series check for A'(x).
        Aprime = sum(sp.Integer(index+1) * terms[index+1] * x**index for index in range(len(terms)-1))
        direct_series_residual = sp.expand(sum(C[j] * sp.diff(Aprime,x,j) for j in range(q)))
        safe_direct = len(terms)-2-(q-1)
        direct_values = [direct_series_residual.coeff(x,e) for e in range(max(0,safe_direct+1))]
        record("direct_ODE_series_residual_zero", all(v==0 for v in direct_values), max([abs(int(v)) for v in direct_values] or [0]))
    else:
        record("direct_ODE_status_valid", direct.get("status") == "not_run" and not direct.get("requested", False), direct)

    elapsed = time.perf_counter() - started
    passed = sum(int(value["pass"]) for value in checks.values())
    say("PASS", f"{passed}/{len(checks)} exact checks in {elapsed:.3f}s")
    return {
        "format": "RELAY-CT-validation-v0.2",
        "q": q,
        "source": str(json_path),
        "pass": passed == len(checks),
        "passed_checks": passed,
        "total_checks": len(checks),
        "elapsed_seconds": elapsed,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_json", type=Path)
    args = parser.parse_args()
    report = validate_case(args.case_json.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
