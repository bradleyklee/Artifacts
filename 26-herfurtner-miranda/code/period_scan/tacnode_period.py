#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = ROOT / "examples" / "data" / "tacnode_period_result.json"
REFERENCE = ROOT / "examples" / "data" / "models_11_release.json"
E = sp.symbols("E")


def convolution(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def circle_moment(a: int, b: int) -> Fraction:
    return Fraction(
        math.factorial(2 * a) * math.factorial(2 * b),
        4 ** (a + b) * math.factorial(a) * math.factorial(b) * math.factorial(a + b),
    )


def average_homogeneous(coefficients: list[Fraction], degree: int) -> Fraction:
    return sum(
        coefficient * circle_moment(p_power, degree - p_power)
        for p_power, coefficient in enumerate(coefficients)
    )


def coefficients(g3_squared: list[Fraction], g4: list[Fraction], max_n: int) -> list[Fraction]:
    """Exact quartic period coefficients using u=p^2 and v=q^2."""
    powers3 = [[Fraction(1)]]
    powers4 = [[Fraction(1)]]
    for _ in range(max_n):
        powers3.append(convolution(powers3[-1], g3_squared))
        powers4.append(convolution(powers4[-1], g4))

    values: list[Fraction] = []
    for n in range(max_n + 1):
        total = Fraction(0)
        for m in range(n + 1):
            polynomial = convolution(powers3[m], powers4[n - m])
            degree = 2 * n + m
            multiplier = Fraction(
                (-1) ** (n - m) * math.factorial(2 * n + m),
                math.factorial(n) * math.factorial(2 * m) * math.factorial(n - m),
            )
            total += multiplier * average_homogeneous(polynomial, degree)
        values.append(total)
    return values


def ode_polynomials_T1() -> list[sp.Expr]:
    return [
        6 * (20 * E**4 + 117 * E**3 + 741 * E**2 - 12004 * E + 5168),
        3 * (464 * E**5 - 1656 * E**4 + 23289 * E**3 - 282691 * E**2 + 80924 * E + 1584),
        4 * (352 * E**6 - 3824 * E**5 + 14846 * E**4 - 212072 * E**3 + 37381 * E**2 + 5000 * E - 448),
        4 * E * (4 * E + 1) * (4 * E**2 - 71 * E + 8) * (4 * E**3 + E**2 + 135 * E - 28),
    ]


def residuals(sequence: list[Fraction], polynomials: list[sp.Expr]) -> list[sp.Rational]:
    max_order = len(polynomials) - 1
    valid_count = len(sequence) - max_order
    out: list[sp.Rational] = []
    for power in range(valid_count):
        total = sp.S.Zero
        for order, polynomial in enumerate(polynomials):
            for (j,), coefficient in sp.Poly(polynomial, E).terms():
                n = power - j + order
                if n < order or n >= len(sequence):
                    continue
                falling = math.factorial(n) // math.factorial(n - order)
                value = sequence[n]
                total += coefficient * falling * sp.Rational(value.numerator, value.denominator)
        out.append(sp.factor(total))
    return out


def scaled_integers(values: list[Fraction], scale: int) -> list[str]:
    scaled = [value * scale**n for n, value in enumerate(values)]
    if not all(value.denominator == 1 for value in scaled):
        raise AssertionError(f"scale {scale} failed")
    return [str(value.numerator) for value in scaled]


def main() -> None:
    # T0: s=0, g3=q^3, g4=-q^4/4. The time differential is holomorphic.
    t0_values = coefficients([Fraction(1)], [Fraction(-1, 4)], 30)
    t0_scaled = scaled_integers(t0_values, 32)
    reference = json.loads(REFERENCE.read_text())
    model1 = reference["models"][0]["first_31_coefficients_at_observed_scale"]
    if t0_scaled != model1:
        raise AssertionError("T0 period does not match model 1")

    # T1: s=1, g3=q(2p^2+q^2), g4=q^2(p^2-q^2/4). The time form is third kind.
    t1_values = coefficients(
        [Fraction(1), Fraction(4), Fraction(4)],
        [Fraction(-1, 4), Fraction(1)],
        50,
    )
    t1_scaled = scaled_integers(t1_values, 32)
    polynomials = ode_polynomials_T1()
    checks = residuals(t1_values, polynomials)
    if any(value != 0 for value in checks):
        raise AssertionError("T1 order-three ODE residual is nonzero")

    payload = {
        "fiber_configuration": ["I1", "I1", "I1", "III*"],
        "projected_binary_quartic": "x^4-4*x^3-4*x^2+4*E",
        "models": [
            {
                "model_id": "T0",
                "hamiltonian_2H": "p^2+q^2+q^3-q^4/4",
                "time_form": "holomorphic",
                "scale_M": 32,
                "integer_coefficients_t": t0_scaled,
                "period_identification": "exactly matches baseline model 1 through all 31 stored terms",
                "proof_route": (
                    "T0 has the same c4, c6 and normalized initial value as model 1; the stored "
                    "coefficient formula also gives termwise equality. The existing model-1 Laurent "
                    "polynomial and certificate therefore cover this new plane presentation."
                ),
                "laurent_status": "covered_by_model_1_Laurent_certificate",
            },
            {
                "model_id": "T1",
                "hamiltonian_2H": "p^2+q^2+2*p^2*q+q^3+p^2*q^2-q^4/4",
                "time_form": "meromorphic_third_kind",
                "scale_M": 32,
                "integer_coefficients_t": t1_scaled,
                "ode_E": {f"P{order}": sp.sstr(sp.factor(poly)) for order, poly in enumerate(polynomials)},
                "ode_convention": "P3(E)*Pi''' + P2(E)*Pi'' + P1(E)*Pi' + P0(E)*Pi = 0",
                "verified_series_equations": len(checks),
                "laurent_status": "open",
            },
        ],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", OUTPUT)
    print("T0 first scaled terms", t0_scaled[:8])
    print("T1 first scaled terms", t1_scaled[:8])
    print("T1 verified ODE equations", len(checks))


if __name__ == "__main__":
    main()
