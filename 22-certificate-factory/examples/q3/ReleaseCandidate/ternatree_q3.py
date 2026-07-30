#!/usr/bin/env python3
"""Derive the A120590 recurrence, terms, and ODE from fixed q=3 data."""

from __future__ import annotations

import argparse
import math
from typing import Iterable

import sympy as sp


def lcm_expr(values: Iterable[sp.Expr]) -> sp.Expr:
    result = sp.Integer(1)
    for value in values:
        result = sp.lcm(result, sp.sympify(value))
    return result


def lower(U: sp.Matrix, V: sp.Matrix, J: sp.Matrix,
          w: sp.Matrix, m: sp.Expr) -> sp.Matrix:
    b = V * w
    return sp.simplify(U * w - (J * b) / m)


def normalize3(p0: sp.Expr, p1: sp.Expr, p2: sp.Expr,
               n: sp.Symbol) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    values = [sp.together(p0), sp.together(p1), sp.together(p2)]
    denoms = [sp.fraction(value)[1] for value in values]
    common = lcm_expr(denoms)
    q = [sp.expand(sp.cancel(common * value)) for value in values]

    poly_gcd = sp.gcd(sp.gcd(q[0], q[1]), q[2])
    if poly_gcd != 0:
        q = [sp.expand(sp.cancel(value / poly_gcd)) for value in q]

    coeff_denoms: list[sp.Expr] = []
    for value in q:
        coeff_denoms.extend(
            sp.fraction(c)[1] for c in sp.Poly(value, n).all_coeffs()
        )
    common_coeff = lcm_expr(coeff_denoms)
    q = [sp.expand(common_coeff * value) for value in q]

    integer_coeffs: list[int] = []
    for value in q:
        integer_coeffs.extend(
            abs(int(c)) for c in sp.Poly(value, n).all_coeffs() if c != 0
        )
    content = 0
    for coeff in integer_coeffs:
        content = math.gcd(content, coeff)
    if content > 1:
        q = [sp.expand(value / content) for value in q]

    if sp.Poly(q[2], n).LC() < 0:
        q = [-value for value in q]
    return tuple(sp.factor(value) for value in q)


def cancel3(X: sp.Matrix, n: sp.Symbol
            ) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    p0 = X[0, 1] * X[1, 2] - X[0, 2] * X[1, 1]
    p1 = X[0, 2] * X[1, 0] - X[0, 0] * X[1, 2]
    p2 = X[0, 0] * X[1, 1] - X[0, 1] * X[1, 0]
    return normalize3(p0, p1, p2, n)


def apply2(P: sp.Expr, r: int, n: sp.Symbol, x: sp.Symbol,
           A: sp.Symbol, Ap: sp.Symbol, App: sp.Symbol) -> sp.Expr:
    poly = sp.Poly(sp.expand(P), n)
    a = poly.coeff_monomial(n**2)
    b = poly.coeff_monomial(n)
    c = poly.coeff_monomial(1)
    return (
        a * (x**2 * App + (1 - 2 * r) * x * Ap + r**2 * A)
        + b * (x * Ap - r * A)
        + c * A
    )


def make_ode(P0: sp.Expr, P1: sp.Expr, P2: sp.Expr,
             n: sp.Symbol, x: sp.Symbol
             ) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    A, Ap, App = sp.symbols("A Ap App")
    L = (
        x**2 * apply2(P0, 0, n, x, A, Ap, App)
        + x * apply2(P1, 1, n, x, A, Ap, App)
        + apply2(P2, 2, n, x, A, Ap, App)
    )
    L = sp.expand(sp.cancel(L / x**2))
    coeffs = (
        sp.factor(L.coeff(App)),
        sp.factor(L.coeff(Ap)),
        sp.factor(L.coeff(A)),
    )
    if sp.Poly(coeffs[0], x).LC() < 0:
        coeffs = tuple(-value for value in coeffs)
    return coeffs


def exact_integer_quotient(numer: sp.Expr, denom: sp.Expr) -> int:
    value = sp.cancel(sp.sympify(numer) / sp.sympify(denom))
    if value.is_Integer is not True:
        raise ArithmeticError(f"nonintegral quotient: ({numer})/({denom})")
    return int(value)


def run_q3(N: int) -> dict[str, object]:
    if N < 2:
        raise ValueError("N must be at least 2")

    n, x = sp.symbols("n x")
    U = sp.Rational(1, 13) * sp.Matrix(
        [[153, 24, 3], [72, 9, 6], [0, 0, 0]]
    )
    V = sp.Rational(1, 13) * sp.Matrix(
        [[-13, 0, 0], [75, 11, 3], [24, 3, 2]]
    )
    J = sp.Matrix([[0, 1, 0], [0, 0, 2], [0, 0, 0]])
    e = sp.Matrix([1, 0, 0])

    c0 = e
    c1 = sp.simplify((n / (n + 1)) * lower(U, V, J, e, n))
    c2 = sp.simplify(
        (n / (n + 2)) * lower(U, V, J, lower(U, V, J, e, n + 1), n)
    )
    X = sp.simplify(sp.Matrix.hstack(c0, c1, c2)[:2, :])
    P0, P1, P2 = cancel3(X, n)

    if sp.simplify(X * sp.Matrix([P0, P1, P2])) != sp.zeros(2, 1):
        raise AssertionError("X*P is not zero")

    u = sp.symbols("u")
    rho = u * (1 - 3 * u - u**2)
    certificate_numerator = (
        -9 * n * u**4 - 36 * n * u**3 + 6 * n * u**2
        + 84 * n * u - 13 * n - 3 * u**4 - 12 * u**3
        - 6 * u**2 + 3 * u
    )
    certificate_residual = sp.expand(
        P0 * rho**2 + n * P1 * rho / (n + 1) + n * P2 / (n + 2)
        - (sp.diff(certificate_numerator, u) * rho
           - (n + 1) * certificate_numerator * sp.diff(rho, u))
    )
    if sp.factor(certificate_residual) != 0:
        raise AssertionError("exact certificate identity failed")
    certificate = sp.factor(certificate_numerator / rho)

    terms = [0] * (N + 1)
    terms[0] = 1
    terms[1] = exact_integer_quotient(1, 4 - 3 * terms[0] ** 2)
    terms[2] = exact_integer_quotient(
        3 * terms[0] * terms[1] ** 2,
        4 - 3 * terms[0] ** 2,
    )
    for k in range(1, N - 1):
        numer = -P0.subs(n, k) * terms[k] - P1.subs(n, k) * terms[k + 1]
        denom = P2.subs(n, k)
        terms[k + 2] = exact_integer_quotient(numer, denom)

    S = sum(sp.Integer(terms[k]) * x**k for k in range(N + 1))
    cubic = sp.Poly(sp.expand(4 * S - 3 - x - S**3), x)
    if any(cubic.nth(k) != 0 for k in range(N + 1)):
        raise AssertionError("truncated series fails the cubic check")

    ode = make_ode(P0, P1, P2, n, x)
    residual = sp.Poly(
        sp.expand(ode[0] * sp.diff(S, x, 2)
                  + ode[1] * sp.diff(S, x) + ode[2] * S),
        x,
    )
    if any(residual.nth(k) != 0 for k in range(N - 1)):
        raise AssertionError("truncated series fails the ODE check")

    return {
        "n": n,
        "x": x,
        "X": X,
        "P": (P0, P1, P2),
        "certificate": certificate,
        "terms": terms,
        "ode": ode,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("N", nargs="?", type=int, default=30)
    args = parser.parse_args()

    result = run_q3(args.N)
    n = result["n"]
    P0, P1, P2 = result["P"]
    c2, c1, c0 = result["ode"]

    print("A120590 ternatree q=3")
    print(f"N = {args.N}")
    print("X*P check: PASS")
    print("exact certificate identity: PASS")
    print("exact recurrence divisions: PASS")
    print("cubic series check: PASS")
    print("ODE series check: PASS")
    print()
    print("Factored recurrence coefficients:")
    print(f"P0(n) = {P0}")
    print(f"P1(n) = {P1}")
    print(f"P2(n) = {P2}")
    print()
    print("Certificate:")
    print(f"R(n,u) = {result['certificate']}")
    print()
    print("Expanded recurrence coefficients:")
    print(f"P0(n) = {sp.expand(P0)}")
    print(f"P1(n) = {sp.expand(P1)}")
    print(f"P2(n) = {sp.expand(P2)}")
    print()
    print("ODE:")
    print(f"({c2})*A''(x) + ({c1})*A'(x) + ({c0})*A(x) = 0")
    print("A(0) = 1, A'(0) = 1")
    print()
    print("Terms:")
    for index, value in enumerate(result["terms"]):
        print(f"a({index}) = {value}")


if __name__ == "__main__":
    main()
