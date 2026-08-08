#!/usr/bin/env python3
"""Verify the Edwards quartic addition law from its invariant differential.

Curve:
    x^2 + y^2 = 1 + d*x^2*y^2.
Identity: (0,1).
Invariant differential (up to a constant):
    omega = dx / (2*y*(1-d*x^2)).
"""
from __future__ import annotations

import json
from pathlib import Path
import sympy as sp


def main() -> None:
    d = sp.symbols("d")
    x1, y1, x2, y2 = sp.symbols("x1 y1 x2 y2")

    def F(x, y):
        return x**2 + y**2 - 1 - d*x**2*y**2

    def Fx(x, y):
        return 2*x*(1-d*y**2)

    def Fy(x, y):
        return 2*y*(1-d*x**2)

    den_plus = 1 + d*x1*x2*y1*y2
    den_minus = 1 - d*x1*x2*y1*y2
    X = sp.factor((x1*y2 + y1*x2)/den_plus)
    Y = sp.factor((y1*y2 - x1*x2)/den_minus)

    def delta1(expr):
        return sp.diff(expr, x1) - Fx(x1, y1)/Fy(x1, y1)*sp.diff(expr, y1)

    def delta2(expr):
        return sp.diff(expr, x2) - Fx(x2, y2)/Fy(x2, y2)*sp.diff(expr, y2)

    r1 = sp.together(delta1(X)*Fy(x1, y1) - Fy(X, Y))
    r2 = sp.together(delta2(X)*Fy(x2, y2) - Fy(X, Y))

    G = sp.groebner([F(x1,y1), F(x2,y2)], y1, y2, x1, x2, order="lex")
    curve_rem = sp.factor(G.reduce(sp.together(F(X,Y)).as_numer_denom()[0])[1])
    r1_rem = sp.factor(G.reduce(sp.together(r1).as_numer_denom()[0])[1])
    r2_rem = sp.factor(G.reduce(sp.together(r2).as_numer_denom()[0])[1])

    assert curve_rem == 0
    assert r1_rem == 0
    assert r2_rem == 0

    # Identity and doubling formulas.
    identity_X = sp.simplify(X.subs({x2:0, y2:1}) - x1)
    identity_Y = sp.simplify(Y.subs({x2:0, y2:1}) - y1)
    assert identity_X == 0 and identity_Y == 0

    X2 = sp.factor(X.subs({x2:x1, y2:y1}))
    Y2 = sp.factor(Y.subs({x2:x1, y2:y1}))

    out = {
        "curve": "x^2 + y^2 - 1 - d*x^2*y^2",
        "identity": ["0", "1"],
        "invariant_differential": "dx/(2*y*(1-d*x^2))",
        "x_sum": str(X),
        "y_sum": str(Y),
        "x_double": str(X2),
        "y_double": str(Y2),
        "curve_closure_remainder": str(curve_rem),
        "differential_residual_1_remainder": str(r1_rem),
        "differential_residual_2_remainder": str(r2_rem),
        "status": "PASS",
    }
    path = Path(__file__).with_name("edwards_quartic_verification.json")
    path.write_text(json.dumps(out, indent=2) + "\n")
    print("PASS: Edwards quartic addition and invariant differential identity")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
