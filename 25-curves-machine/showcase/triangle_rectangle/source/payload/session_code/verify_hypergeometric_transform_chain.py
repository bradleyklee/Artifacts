#!/usr/bin/env python3
"""Verify the rescaled Jacobi/signature-four and modular j-line pullbacks exactly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "analysis" / "hypergeometric_transform_chain.json"


def verify_pullback(alpha, p2, p1, p0, aa, bb, xx, gauge):
    yxx_yx = ((aa + bb + 1) * xx - 1) / (xx * (1 - xx))
    yxx_y = aa * bb / (xx * (1 - xx))
    xp = sp.diff(xx, alpha)
    xpp = sp.diff(xp, alpha)
    gp = sp.diff(gauge, alpha)
    gpp = sp.diff(gp, alpha)
    coeff_y = sp.factor(sp.together(
        p2 * (gpp + gauge * xp**2 * yxx_y) + p1 * gp + p0 * gauge
    ))
    coeff_yx = sp.factor(sp.together(
        p2 * (2 * gp * xp + gauge * xpp + gauge * xp**2 * yxx_yx)
        + p1 * gauge * xp
    ))
    return sp.simplify(coeff_y), sp.simplify(coeff_yx)


def derive() -> dict[str, object]:
    alpha = sp.symbols("alpha")

    p2 = alpha * (alpha - 1) * (3 * alpha - 8) * (9 * alpha + 16)
    p1 = 54 * alpha**3 - 195 * alpha**2 - 112 * alpha + 128
    p0 = sp.Rational(3, 4) * alpha * (9 * alpha - 64)

    s4 = sp.factor(alpha * (9 * alpha + 16) / (3 * alpha + 2) ** 2)
    g4 = sp.sqrt(2 / (2 + 3 * alpha))
    s4_y, s4_yx = verify_pullback(
        alpha, p2, p1, p0,
        sp.Rational(1, 4), sp.Rational(3, 4), s4, g4,
    )
    assert (s4_y, s4_yx) == (0, 0)

    chi = sp.factor(
        -108 * alpha**2 * (alpha - 1) * (9 * alpha + 16) ** 2
        / (9 * alpha**2 + 16) ** 3
    )
    gj = (1 + sp.Rational(9, 16) * alpha**2) ** sp.Rational(-1, 4)
    j_y, j_yx = verify_pullback(
        alpha, p2, p1, p0,
        sp.Rational(1, 12), sp.Rational(5, 12), chi, gj,
    )
    assert (j_y, j_yx) == (0, 0)

    root = sp.sqrt(alpha * (16 + 9 * alpha))
    r_plus = (2 + 3 * alpha + root) / 2
    r_minus = (2 + 3 * alpha - root) / 2
    jacobi_m = sp.factor(1 - r_minus / r_plus)
    s4_from_m = sp.factor((jacobi_m / (2 - jacobi_m)) ** 2)
    assert sp.simplify(s4_from_m - s4) == 0

    legendre_lambda = sp.factor(
        (3 * alpha + 2 - 2 * sp.sqrt(1 - alpha))
        / (3 * alpha + 2 + 2 * sp.sqrt(1 - alpha))
    )
    chi_from_lambda = sp.factor(
        27 * legendre_lambda**2 * (1 - legendre_lambda) ** 2
        / (4 * (1 - legendre_lambda + legendre_lambda**2) ** 3)
    )
    assert sp.simplify(chi_from_lambda - chi) == 0

    alpha_star = 4 * (sp.sqrt(6) - 2) / 3
    assert sp.simplify(chi.subs(alpha, alpha_star) - 1) == 0
    assert sp.simplify(legendre_lambda.subs(alpha, alpha_star) - sp.Rational(1, 2)) == 0
    assert sp.simplify(s4.subs(alpha, 1) - 1) == 0

    return {
        "normalization": {
            "phase_coordinates": "p_new=2*p_old, q_new=2*q_old",
            "energy": "alpha_new=4*alpha_old",
            "interval": "0<=alpha<1",
        },
        "target_ode": {"P2": str(p2), "P1": str(p1), "P0": str(p0)},
        "signature_4_form": {
            "formula": "T=sqrt(2/(2+3*alpha))*2F1(1/4,3/4;1;s4)",
            "s4": str(s4),
            "endpoint": "s4(1)=1",
            "pullback_coefficient_of_y": str(s4_y),
            "pullback_coefficient_of_y_x": str(s4_yx),
        },
        "j_line_form": {
            "local_germ_formula": "T=(1+9*alpha^2/16)^(-1/4)*2F1(1/12,5/12;1;chi)",
            "scope": "Principal 2F1 value gives the alpha=0 branch through alpha_star only; use the continued Eisenstein root after the fold.",
            "alpha_star": str(alpha_star),
            "chi": str(chi),
            "j": str(sp.factor(1728 / chi)),
            "pullback_coefficient_of_y": str(j_y),
            "pullback_coefficient_of_y_x": str(j_yx),
        },
        "branch_parameters": {
            "r_plus": str(r_plus),
            "r_minus": str(r_minus),
            "legendre_lambda": str(legendre_lambda),
            "direct_jacobi_modulus_m": str(jacobi_m),
            "signature_4_parameter_from_m": str(s4_from_m),
            "chi_from_legendre_lambda": str(chi_from_lambda),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    result = derive()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("ALL EXACT PULLBACK CHECKS PASS")
    print("s4 =", result["signature_4_form"]["s4"])
    print("chi =", result["j_line_form"]["chi"])
    print("j =", result["j_line_form"]["j"])
    print("wrote", args.json)


if __name__ == "__main__":
    main()
