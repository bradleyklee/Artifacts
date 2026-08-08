#!/usr/bin/env python3
"""Derive and verify the addition law on a general Weierstrass cubic.

Curve:
    F(x,y) = y^2 + a1*x*y + a3*y - x^3 - a2*x^2 - a4*x - a6 = 0.
Invariant differential:
    omega = dx / (2*y + a1*x + a3).

For two generic points P1,P2, derive the chord formula and verify exactly:
    m(P1,P2) lies on F=0,
    m^* omega = pr1^* omega + pr2^* omega.
"""
from __future__ import annotations

import json
from pathlib import Path
import sympy as sp


def main() -> None:
    a1, a2, a3, a4, a6 = sp.symbols("a1 a2 a3 a4 a6")
    x1, y1, x2, y2 = sp.symbols("x1 y1 x2 y2")

    def F(x, y):
        return y**2 + a1*x*y + a3*y - x**3 - a2*x**2 - a4*x - a6

    def Fy(x, y):
        return 2*y + a1*x + a3

    def tangent_yprime(x, y):
        # dy/dx along F=0.
        return (3*x**2 + 2*a2*x + a4 - a1*y) / Fy(x, y)

    # Line y = lambda*x + nu through P1 and P2.
    lam = sp.cancel((y2 - y1)/(x2 - x1))
    nu = sp.cancel((y1*x2 - y2*x1)/(x2 - x1))

    # Vieta gives the third line intersection R; negate R in the
    # generalized Weierstrass involution to obtain P1+P2.
    x3 = sp.factor(lam**2 + a1*lam - a2 - x1 - x2)
    y3 = sp.factor(-(lam + a1)*x3 - nu - a3)

    def delta1(expr):
        return sp.diff(expr, x1) + tangent_yprime(x1, y1)*sp.diff(expr, y1)

    def delta2(expr):
        return sp.diff(expr, x2) + tangent_yprime(x2, y2)*sp.diff(expr, y2)

    # Differential residuals.  These are equivalent to the coefficients
    # of dx1 and dx2 in m^*omega - omega1 - omega2.
    r1 = sp.factor(sp.together(delta1(x3)*Fy(x1, y1) - Fy(x3, y3)))
    r2 = sp.factor(sp.together(delta2(x3)*Fy(x2, y2) - Fy(x3, y3)))

    F1 = F(x1, y1)
    F2 = F(x2, y2)

    # Exact ideal reduction checks.
    G = sp.groebner([F1, F2], y1, y2, x1, x2, order="lex")
    curve_num = sp.together(F(x3, y3)).as_numer_denom()[0]
    curve_rem = sp.factor(G.reduce(curve_num)[1])
    r1_num = sp.together(r1).as_numer_denom()[0]
    r2_num = sp.together(r2).as_numer_denom()[0]
    r1_rem = sp.factor(G.reduce(r1_num)[1])
    r2_rem = sp.factor(G.reduce(r2_num)[1])

    assert curve_rem == 0
    assert r1_rem == 0
    assert r2_rem == 0

    # The differential residual has an especially transparent factorization.
    expected_difference = sp.factor(F2 - F1)
    residual_factor = sp.factor(
        (a1*(x1-x2) + 2*(y1-y2))*expected_difference/(x1-x2)**3
    )
    assert sp.factor(r1 - residual_factor) == 0
    assert sp.factor(r2 + residual_factor) == 0

    out = {
        "curve": str(F(sp.Symbol("x"), sp.Symbol("y"))),
        "invariant_differential_denominator": "2*y + a1*x + a3",
        "lambda": str(lam),
        "nu": str(nu),
        "x_sum": str(x3),
        "y_sum": str(y3),
        "curve_closure_remainder": str(curve_rem),
        "differential_residual_1_remainder": str(r1_rem),
        "differential_residual_2_remainder": str(r2_rem),
        "factored_differential_residual_1": str(r1),
        "status": "PASS",
    }
    path = Path(__file__).with_name("cubic_verification.json")
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("PASS: general cubic addition and invariant differential identity")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
