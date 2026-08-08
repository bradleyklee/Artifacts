#!/usr/bin/env python3
"""Derive the generic mu Picard-Fuchs operator and exact certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "analysis" / "general_mu_picard_fuchs.json"


def derive() -> dict[str, object]:
    mu, z, u = sp.symbols("mu z u")

    D = (
        (sp.Rational(1, 4) - sp.Rational(4, 3) * mu) * u**4
        - sp.Rational(1, 3) * u**3
        + (4 * mu * z - sp.Rational(1, 3)) * u**2
        + 2 * z * u
        + sp.Rational(4, 3) * z
    )

    I = (1 + (54 - 216 * mu) * z + 144 * mu**2 * z**2) / 9
    J = (
        2
        + (1080 * mu - 270) * z
        + (-12960 * mu**2 + 5832 * mu - 729) * z**2
        - 3456 * mu**3 * z**3
    ) / 27

    c4, c6 = 4 * I, 4 * J
    delta = sp.expand(c4**3 - c6**2)
    G = sp.expand(2 * c4 * sp.diff(c6, z) - 3 * c6 * sp.diff(c4, z))

    raw_p3 = sp.expand(144 * delta * G)
    raw_p2 = sp.expand(144 * (sp.diff(delta, z) * G - delta * sp.diff(G, z)))
    raw_p1 = sp.expand(
        12 * (sp.diff(delta, z, 2) * G - sp.diff(delta, z) * sp.diff(G, z))
        - 9 * G * c4 * sp.diff(c4, z) ** 2
        + 4 * G * sp.diff(c6, z) ** 2
    )

    common = 4 + (144 * mu - 27) * z
    normalizer = -sp.Rational(27, 8192)
    p3 = sp.factor(normalizer * raw_p3 / common**2)
    p2 = sp.factor(normalizer * raw_p2 / common**2)
    p1 = sp.factor(normalizer * raw_p1 / common**2)

    field = sp.QQ.frac_field(mu)
    gcd = sp.gcd(sp.Poly(p3, z, domain=field), sp.Poly(p2, z, domain=field))
    gcd = sp.gcd(gcd, sp.Poly(p1, z, domain=field))
    assert sp.degree(gcd.as_expr(), z) == 0

    # Exact differential certificate:
    # (P3 d_z^2 + P2 d_z + P1)(du/sqrt(D)) = d_u(R/D^(3/2)).
    Dz = sp.diff(D, z)
    numerator = sp.expand(
        p1 * D**2
        - sp.Rational(1, 2) * p2 * Dz * D
        + sp.Rational(3, 4) * p3 * Dz**2
    )
    coeffs = sp.symbols("r0:7")
    Rtrial = sum(coeffs[j] * u**j for j in range(7))
    equation = sp.expand(
        sp.diff(Rtrial, u) * D
        - sp.Rational(3, 2) * Rtrial * sp.diff(D, u)
        - numerator
    )
    matrix, rhs = sp.linear_eq_to_matrix(sp.Poly(equation, u).all_coeffs(), coeffs)
    solution = list(sp.linsolve((matrix, rhs), coeffs))[0]
    R = sp.factor(Rtrial.subs(dict(zip(coeffs, solution))))
    remainder = sp.cancel(
        sp.diff(R, u) * D
        - sp.Rational(3, 2) * R * sp.diff(D, u)
        - numerator
    )
    assert remainder == 0

    special = {mu: sp.Rational(1, 4)}
    special_p3 = sp.factor(p3.subs(special) / z**2)
    special_p2 = sp.factor(p2.subs(special) / z**2)
    special_p1 = sp.factor(p1.subs(special) / z**2)
    assert special_p3 == z * (3 * z - 2) * (4 * z - 1) * (9 * z + 4)
    assert special_p2 == 216 * z**3 - 195 * z**2 - 28 * z + 8
    assert special_p1 == 3 * z * (9 * z - 16)

    return {
        "convention": "P3(z,mu)*T'' + P2(z,mu)*T' + P1(z,mu)*T = 0",
        "D": str(sp.factor(D)),
        "I": str(sp.factor(I)),
        "J": str(sp.factor(J)),
        "P3_factored": str(p3),
        "P3_expanded": str(sp.expand(p3)),
        "P2": str(sp.expand(p2)),
        "P1": str(sp.expand(p1)),
        "generic_gcd_in_Q(mu)[z]": str(sp.factor(gcd.as_expr())),
        "certificate_degree_in_u": int(sp.degree(R, u)),
        "certificate_R": str(R),
        "certificate_identity_remainder": str(remainder),
        "mu_1_over_4_reduced": {
            "P3": str(special_p3),
            "P2": str(special_p2),
            "P1": str(special_p1),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()

    result = derive()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("P3 =", result["P3_factored"])
    print("P2 =", result["P2"])
    print("P1 =", result["P1"])
    print("generic gcd =", result["generic_gcd_in_Q(mu)[z]"])
    print("certificate degree =", result["certificate_degree_in_u"])
    print("exact certificate: PASS")
    print("wrote", args.json)


if __name__ == "__main__":
    main()
