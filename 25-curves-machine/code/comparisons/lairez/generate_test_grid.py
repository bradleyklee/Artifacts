#!/usr/bin/env python3
"""Generate a reproducible harmonic Hamiltonian benchmark grid."""
from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cases" / "grid"


def real_mode(degree: int) -> str:
    terms = []
    for p_degree in range(0, degree + 1, 2):
        coefficient = comb(degree, p_degree) * (-1) ** (p_degree // 2)
        q_degree = degree - p_degree
        monomial = "*".join(([f"p^{p_degree}"] if p_degree else []) +
                            ([f"q^{q_degree}"] if q_degree else [])) or "1"
        terms.append(f"({coefficient})*{monomial}")
    return " + ".join(terms)


def scaled_mode(degree: int, coefficient: str) -> str:
    return f"({coefficient})*({real_mode(degree)})"


def write_case(name: str, terms: list[dict], group: str,
               expected_order: int | None, klee: dict) -> None:
    energy = "p^2 + q^2"
    for term in terms:
        energy += " + " + scaled_mode(term["degree"], term["coefficient"])
    data = {
        "name": name,
        "description": f"generated {group} harmonic benchmark",
        "benchmark_group": group,
        "variables": ["p", "q"],
        "parameter": "alpha",
        "harmonic_terms": terms,
        "energy_E_equals_2H": energy,
        "klee_config": klee,
        "lairez_input": "2/(E-alpha)",
    }
    coefficients = {term["degree"]: Fraction(term["coefficient"]) for term in terms}
    if 3 in coefficients and 4 in coefficients:
        tau = coefficients[3]**2/coefficients[4]
        data["scaling_invariant_tau_equals_c3_squared_over_c4"] = str(tau)
    if expected_order is not None:
        data["known_operator_order"] = expected_order
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    # Generic mixed quartics: vary the triangle/square balance and overall
    # coefficient height without changing the finite support policy.
    for c3 in ("1/2", "1", "2"):
        for c4 in ("1/8", "1/4", "1/2"):
            tag3, tag4 = c3.replace("/", "_"), c4.replace("/", "_")
            exceptional = c3 == "1" and c4 == "1/4"
            write_case(
                f"quartic_t{tag3}_s{tag4}",
                [{"degree": 3, "mode": 3, "coefficient": c3},
                 {"degree": 4, "mode": 4, "coefficient": c4}],
                "mixed_quartic", 2 if exceptional else None,
                {"order": 2 if exceptional else 4,
                 "q_degree": 9 if exceptional else 21,
                 "p_degrees": [0, 2],
                 "support": "rectangular"})
    # Pure square controls.
    for c4 in ("1/8", "1/4", "1/2"):
        tag4 = c4.replace("/", "_")
        write_case(
            f"quartic_square_{tag4}",
            [{"degree": 4, "mode": 4, "coefficient": c4}],
            "pure_quartic", 2,
            {"order": 2, "q_degree": 9, "p_degrees": [0, 2],
             "support": "rectangular"})
    # Pure hexagon controls. Bound 35 is the first tested bound known to close
    # for coefficient 1/4; other coefficients test stability of that rule.
    for c6 in ("1/8", "1/4", "1/2"):
        tag6 = c6.replace("/", "_")
        write_case(
            f"sextic_hexagon_{tag6}",
            [{"degree": 6, "mode": 6, "coefficient": c6}],
            "pure_sextic", 4,
            {"order": 4, "weight_bound": 35, "p_degrees": [0, 2, 4],
             "support": "even_p_odd_q_weighted"})
    print(OUT)


if __name__ == "__main__":
    main()
