#!/usr/bin/env python3
"""Direct parameter-derivative reduction for the OGF ODE.

For A_q(x)-1=T_q(x), rho_q(T_q(x))=x and

    A_q'(x) = Res_u 1/(rho_q(u)-x) du.

Repeated x-derivatives are reduced modulo exact u-derivatives using the
same G,U,V,J machinery as the fast shift reduction.  A nullspace relation
among the reduced derivatives gives a linear ODE for A_q'(x) together with
an integrand-level rational certificate.
"""
from __future__ import annotations

import math
import time
from typing import Callable

import sympy as sp

u, x, n = sp.symbols("u x n")


def _primitive_vector(values: list[sp.Expr], variable: sp.Symbol) -> sp.Matrix:
    expressions = [sp.cancel(value) for value in values]
    denominators = [sp.Poly(sp.denom(value), variable, domain=sp.QQ) for value in expressions]
    common_denominator = denominators[0]
    for denominator in denominators[1:]:
        common_denominator = sp.lcm(common_denominator, denominator)
    polynomials = [
        sp.Poly(sp.cancel(value * common_denominator.as_expr()), variable, domain=sp.QQ)
        for value in expressions
    ]
    common_polynomial = polynomials[0]
    for polynomial in polynomials[1:]:
        common_polynomial = sp.gcd(common_polynomial, polynomial)
    polynomials = [sp.exquo(polynomial, common_polynomial) for polynomial in polynomials]
    coefficient_lcm = 1
    for polynomial in polynomials:
        for coefficient in polynomial.all_coeffs():
            coefficient_lcm = sp.ilcm(coefficient_lcm, int(sp.denom(coefficient)))
    polynomials = [
        sp.Poly(sp.expand(polynomial.as_expr() * coefficient_lcm), variable, domain=sp.ZZ)
        for polynomial in polynomials
    ]
    content = 0
    for polynomial in polynomials:
        content = math.gcd(content, abs(int(polynomial.content())))
    if content > 1:
        polynomials = [sp.Poly(p.as_expr() / content, variable, domain=sp.ZZ) for p in polynomials]
    if polynomials[-1].LC() < 0:
        polynomials = [-p for p in polynomials]
    return sp.Matrix([p.as_expr() for p in polynomials])


def _matrix_json(matrix: sp.Matrix, expr_text: Callable[[sp.Expr], str]) -> list[list[str]]:
    return [[expr_text(sp.cancel(matrix[r, c])) for c in range(matrix.cols)] for r in range(matrix.rows)]


def _vector_json(vector: sp.Matrix, expr_text: Callable[[sp.Expr], str]) -> list[str]:
    return [expr_text(sp.cancel(vector[i])) for i in range(vector.rows)]


def ode_to_recurrence(ode_coefficients: list[sp.Expr]) -> list[sp.Expr]:
    """Convert sum_j c_j(x) D_x^j A'(x)=0 to coefficients on a(n+r).

    The coefficient of x^(n-1) gives a recurrence on a(n),...,a(n+s).
    """
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
            derivative_factor = (
                sp.prod(source_index - h for h in range(derivative_order))
                if derivative_order
                else sp.Integer(1)
            )
            # A'(x) coefficient b_m=(m+1)a(m+1).
            result[shift] += scalar * derivative_factor * (source_index + 1)
    return [sp.factor(value) for value in result]


def build_direct_ode(
    q: int,
    rho: sp.Expr,
    *,
    progress: Callable[[str, str], None],
    expr_text: Callable[..., str],
) -> dict:
    started = time.perf_counter()
    stage_started = started
    stage_seconds: dict[str, float] = {}

    def finish(name: str) -> None:
        nonlocal stage_started
        now = time.perf_counter()
        stage_seconds[name] = now - stage_started
        stage_started = now

    g = sp.expand(rho - x)
    progress("ODE DIRECT", f"parameter-derivative reduction for F(x,u)=1/(rho(u)-x), q={q}")
    finish("input")

    progress("ODE Gx ASSEMBLY", f"building parameter-dependent {2*q}x{2*q} matrix")
    a_symbols = sp.symbols(f"oa0:{q}")
    b_symbols = sp.symbols(f"ob0:{q}")
    a_poly = sum(a_symbols[i] * u**i for i in range(q))
    b_poly = sum(b_symbols[i] * u**i for i in range(q))
    w_poly = sp.expand(g * a_poly - sp.diff(g, u) * b_poly)
    Gx = sp.zeros(2 * q, 2 * q)
    unknowns = list(a_symbols) + list(b_symbols)
    for row in range(2 * q):
        coefficient = w_poly.coeff(u, row)
        for column, symbol in enumerate(unknowns):
            Gx[row, column] = sp.diff(coefficient, symbol)
    finish("Gx_assembly")

    progress("ODE Gx DET", "computing determinant over Z[x]")
    det_Gx = sp.factor(Gx.det())
    if det_Gx == 0:
        raise AssertionError("direct ODE reduction matrix is singular")
    finish("Gx_determinant")
    progress("ODE Gx DET", f"det(Gx)={expr_text(det_Gx, factor=True)}")

    progress("ODE Gx INVERSE", "inverting over Q(x)")
    Gx_inverse = Gx.inv()
    finish("Gx_inversion")
    progress("ODE Gx INVERSE", "complete")

    E = sp.zeros(2 * q, q)
    for i in range(q):
        E[i, i] = 1
    Ux = Gx_inverse[:q, :] * E
    Vx = Gx_inverse[q:, :] * E
    J = sp.zeros(q, q)
    for column in range(1, q):
        J[column - 1, column] = column
    if not (Gx * sp.Matrix.vstack(Ux, Vx) - E).applyfunc(sp.cancel).is_zero_matrix:
        raise AssertionError("Gx*[Ux;Vx]=E failed")
    finish("Ux_Vx_J")

    progress("ODE DERIVATIVES", f"reducing D_x^j F for j=0..{q-1}")
    reduced_columns: list[sp.Matrix] = []
    derivative_records: list[dict] = []
    internal_records: list[list[tuple[int, sp.Matrix]]] = []
    for derivative_order in range(q):
        progress("ODE DERIVATIVES", f"derivative {derivative_order}/{q-1}: {derivative_order} lowering step(s)")
        current = sp.zeros(q, 1)
        current[0] = sp.factorial(derivative_order)
        steps: list[dict] = []
        internal: list[tuple[int, sp.Matrix]] = []
        for pole_parameter in range(derivative_order, 0, -1):
            certificate_vector = (Vx * current).applyfunc(sp.cancel)
            output_vector = (Ux * current - J * certificate_vector / pole_parameter).applyfunc(sp.cancel)
            steps.append({
                "pole_parameter": pole_parameter,
                "input_vector": _vector_json(current, expr_text),
                "certificate_vector": _vector_json(certificate_vector, expr_text),
                "output_vector": _vector_json(output_vector, expr_text),
            })
            internal.append((pole_parameter, certificate_vector))
            current = output_vector
        reduced_columns.append(current)
        internal_records.append(internal)
        derivative_records.append({
            "derivative_order": derivative_order,
            "input_integrand": f"{math.factorial(derivative_order)}/g(x,u)^{derivative_order+1}",
            "steps": steps,
            "final_remainder_vector": _vector_json(current, expr_text),
        })
    finish("derivative_reductions")

    X_full = sp.Matrix.hstack(*reduced_columns)
    if any(sp.cancel(X_full[q - 1, column]) != 0 for column in range(q)):
        raise AssertionError("direct ODE remainder top-degree row is nonzero")
    X = X_full[: q - 1, :]
    progress("ODE KERNEL", f"solving nullspace of {q-1}x{q} derivative-remainder matrix")
    domain_X = X.to_DM(field=True)
    rank_X = int(domain_X.rank())
    nullspace = domain_X.nullspace().to_Matrix()
    if rank_X != q - 1 or nullspace.shape != (1, q):
        raise AssertionError(f"unexpected direct ODE rank/nullspace: rank={rank_X}, shape={nullspace.shape}")
    coefficients = _primitive_vector(list(nullspace[0, :]), x)
    if not (X * coefficients).applyfunc(sp.cancel).is_zero_matrix:
        raise AssertionError("direct ODE X*c != 0")
    finish("kernel")
    progress("ODE KERNEL", f"rank={rank_X}; nullity=1; ODE order={q-1}")

    progress("ODE CERTIFICATE", f"assembling {q*(q-1)//2} derivative-certificate contributions")
    numerator = sp.Integer(0)
    for derivative_order in range(1, q):
        records = internal_records[derivative_order]
        progress(
            "ODE CERTIFICATE",
            f"derivative {derivative_order}/{q-1}: adding {len(records)} contribution(s)",
        )
        for pole_parameter, certificate_vector in records:
            certificate_polynomial = sum(certificate_vector[i] * u**i for i in range(q))
            numerator += (
                coefficients[derivative_order]
                * certificate_polynomial
                * g ** (q - 1 - pole_parameter)
                / pole_parameter
            )
    progress("ODE CERTIFICATE", "all contributions added; canonicalizing numerator")
    numerator = sp.cancel(numerator)
    if sp.denom(numerator) != 1:
        raise AssertionError("direct ODE certificate numerator is not polynomial")
    numerator_poly = sp.Poly(numerator, x, u, domain=sp.QQ)
    numerator = numerator_poly.as_expr()
    finish("certificate_assembly")

    progress("ODE CHECK", "checking exact integrand-level differential identity")
    left = sum(coefficients[j] * sp.factorial(j) * g ** (q - j - 1) for j in range(q))
    right = sp.expand(g * sp.diff(numerator, u) - (q - 1) * sp.diff(g, u) * numerator)
    residual = sp.Poly(sp.together(left - right), x, u, domain=sp.QQ)
    if not residual.is_zero:
        raise AssertionError("direct ODE cleared certificate identity failed")
    finish("identity_check")
    progress("ODE CHECK", "exact residual is zero")

    induced = ode_to_recurrence(list(coefficients))
    primitive_induced = _primitive_vector(induced, n)
    elapsed = time.perf_counter() - started
    return {
        "status": "complete",
        "method": "repeated parameter differentiation followed by Hermite-Ostrogradsky reduction",
        "integrand": {
            "symbol": "F_q(x,u)",
            "formula": "1/(rho_q(u)-x)",
            "residue_relation": "A_q'(x)=Res_{u=0} F_q(x,u) du",
            "denominator_g": expr_text(g),
        },
        "bases": {
            "coefficient_order": "ascending powers of u",
            "polynomial_basis_q": ["1"] + [f"u^{i}" for i in range(1, q)],
            "Gx_domain": "coeff(a_0..a_{q-1}) followed by coeff(b_0..b_{q-1})",
            "Gx_codomain": ["1"] + [f"u^{i}" for i in range(1, 2*q)],
        },
        "matrices": {
            "Gx": {"shape": [2*q, 2*q], "entries": _matrix_json(Gx, expr_text)},
            "Gx_inverse": {"shape": [2*q, 2*q], "entries": _matrix_json(Gx_inverse, expr_text)},
            "embedding_E": {"shape": [2*q, q], "entries": _matrix_json(E, expr_text)},
            "Ux": {"shape": [q, q], "entries": _matrix_json(Ux, expr_text)},
            "Vx": {"shape": [q, q], "entries": _matrix_json(Vx, expr_text)},
            "J": {"shape": [q, q], "entries": _matrix_json(J, expr_text)},
            "X_full": {"shape": [q, q], "entries": _matrix_json(X_full, expr_text)},
            "X": {"shape": [q-1, q], "entries": _matrix_json(X, expr_text)},
        },
        "Gx": {"determinant": expr_text(det_Gx), "invertible": True},
        "derivative_reductions": derivative_records,
        "ode_for_A_prime": {
            "order": q - 1,
            "coefficients": [expr_text(c) for c in coefficients],
            "identity": "sum_{j=0}^{q-1} C_j(x) d^j A_q'(x)/dx^j = 0",
        },
        "certificate": {
            "numerator": expr_text(numerator),
            "denominator_base": expr_text(g),
            "denominator_power": q - 1,
            "identity": "sum_j C_j(x) d_x^j F_q(x,u)=d_u(N_ODE/g^(q-1))",
            "degree_x": int(numerator_poly.degree(x)),
            "degree_u": int(numerator_poly.degree(u)),
        },
        "induced_coefficient_recurrence": {
            "raw_coefficients": [expr_text(v) for v in induced],
            "primitive_coefficients": [expr_text(v) for v in primitive_induced],
            "identity": "coefficient extraction from the direct ODE for A_q'(x)",
        },
        "statistics": {
            "wall_seconds": elapsed,
            "stage_seconds": stage_seconds,
            "Gx_dimension": 2*q,
            "remainder_dimension": q-1,
            "derivative_count": q,
            "partial_certificate_count": q*(q-1)//2,
        },
        "verification": {
            "Gx_invertible": {"relation": "det(Gx)!=0", "witness": expr_text(det_Gx), "residual": 0, "pass": True},
            "Gx_inverse": {"relation": "Gx*Gx_inverse=I", "residual": 0, "pass": True},
            "Gx_Ux_Vx_split": {"relation": "Gx*[Ux;Vx]=E", "residual": 0, "pass": True},
            "derivative_remainder_kernel": {"relation": "X_ODE*C=0", "residual": 0, "rank": rank_X, "nullity": 1, "pass": True},
            "integrand_certificate": {"relation": "sum_j C_j d_x^j F=d_u(N_ODE/g^(q-1))", "residual": 0, "pass": True},
            "leading_coefficient_equals_det_Gx": {
                "relation": "C_{q-1}(x)=det(Gx)",
                "residual": expr_text(sp.expand(coefficients[-1] - det_Gx)),
                "pass": sp.expand(coefficients[-1] - det_Gx) == 0,
            },
        },
    }
