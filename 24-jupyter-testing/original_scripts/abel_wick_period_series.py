#!/usr/bin/env python3
"""Exact mapped-area period coefficients for Artifact 24's Abel-Wick lobes.

This is the Abel-Wick companion to ``compute_mesh_area_series.py``.  It uses
bounded action-angle coordinates around each triple-point preimage and computes
coefficients of

    Phi_i(s) = d/ds [ A_i(s) / (pi J_i(0)) ]
             = sum_{k >= 0} b_{i,k} s^k.

The source oval is

    (X^2 + Y^2) * (1 + 2 X/(3 sqrt(3))) <= s.

For the green family use Y=V; for yellow/blue use
Y=sqrt(3/10153) V.  Together with X=2U/(3sqrt(3)), these substitutions make
the normalized Gram determinants rational polynomials in U,V.  The square-root
homogeneous recurrence and angular beta moments are then evaluated exactly.
"""
from __future__ import annotations

import argparse
import csv
import math
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.polys.densearith import dup_add, dup_mul
from sympy.polys.densebasic import dup_strip
from sympy.polys.domains import QQ

X, Y = sp.symbols("X Y", real=True)
SQRT3 = sp.sqrt(3)
A_CUBIC = sp.Rational(2, 3) / SQRT3
RATIONAL_Y_DENOMINATOR = 10153

FAMILY_NAMES = ("green", "yellow", "blue")
FAMILY_INDEX = {name: i for i, name in enumerate(FAMILY_NAMES)}
SCALES = {
    "green": sp.Integer(71_912_664),
    "yellow": sp.Integer(943_148_703_570_448_617_216),
    "blue": sp.Integer(943_148_703_570_448_617_216),
}

CENTROID = sp.Matrix([0, 0, sp.Rational(17, 4)])
P_VECTORS = (
    sp.Matrix([0, 0, -3 * SQRT3 / 2]),
    sp.Matrix([SQRT3 / 3, -SQRT3 / 2, 3 * SQRT3 / 4]),
    sp.Matrix([-SQRT3 / 3, SQRT3 / 2, 3 * SQRT3 / 4]),
)
K = sp.sqrt(sp.Rational(781, 13))
Q_VECTORS = (
    sp.Matrix([-1, -sp.Rational(2, 3), 0]),
    sp.Matrix([-K / 4, -K / 6, 0]),
    sp.Matrix([-K / 4, -K / 6, 0]),
)


def polynomial_map_symbolic(point: sp.Matrix) -> sp.Matrix:
    """Levent Alpoge's polynomial map F=(P,Q,R)."""
    x, y, z = point
    xy = x * y
    return sp.Matrix([
        (1 + xy) ** 3 * z + y**2 * (1 + xy) * (4 + 3 * xy),
        y + 3 * x * (1 + xy) ** 2 * z + 3 * x * y**2 * (4 + 3 * xy),
        2 * x - 3 * x**2 * y - x**3 * z,
    ])


def local_source_embedding(family: int) -> sp.Matrix:
    """Affine source-plane embedding in local bounded coordinates X,Y."""
    p = SQRT3 + X
    q = Y / SQRT3
    return CENTROID + p * P_VECTORS[family] + q * Q_VECTORS[family]


def local_range_map(family: int) -> sp.Matrix:
    """Exact polynomial map R_i(X,Y)=F(E_i(X,Y))."""
    return sp.expand(polynomial_map_symbolic(local_source_embedding(family)))


def gram_determinant(family: int) -> tuple[sp.Expr, sp.Expr]:
    """Return det(G_i) and its value at the center."""
    range_map = local_range_map(family)
    rx = range_map.diff(X)
    ry = range_map.diff(Y)
    cross = sp.expand(rx.cross(ry))
    determinant = sp.expand(cross.dot(cross))
    center = sp.factor(determinant.subs({X: 0, Y: 0}))
    return determinant, center


def center_density(family: int) -> sp.Expr:
    return sp.sqrt(gram_determinant(family)[1])


RationalElement = Any

def _mpq(value: object) -> RationalElement:
    """Convert through SymPy's active QQ backend.

    Binder may use gmpy2.mpq while a plain Python install uses PythonMPQ.
    Constructing one private class directly can mix incompatible rationals.
    """
    return QQ.convert(sp.Rational(value))


def rationalized_gram_parts(family: int) -> tuple[dict[int, list[RationalElement]], sp.Expr]:
    """Homogeneous parts of det(G_i)/det(G_i)(0) in rational U,V coordinates.

    Dense univariate arrays are stored high-degree first, as expected by
    SymPy's dense polynomial arithmetic.
    """
    determinant, center = gram_determinant(family)
    U, V = sp.symbols("U V", real=True)
    y_scale = (
        sp.Integer(1)
        if family == 0
        else sp.sqrt(3) / sp.sqrt(RATIONAL_Y_DENOMINATOR)
    )
    rationalized = sp.expand(
        (determinant / center).subs({X: A_CUBIC * U, Y: y_scale * V})
    )
    polynomial = sp.Poly(rationalized, U, V, extension=True)

    parts: dict[int, list[RationalElement]] = {}
    for (u_power, v_power), coefficient in polynomial.terms():
        if not coefficient.is_Rational:
            raise AssertionError(
                f"family={family}, monomial=({u_power},{v_power}), "
                f"non-rational coefficient={coefficient}"
            )
        degree = u_power + v_power
        row = parts.setdefault(degree, [QQ.zero] * (degree + 1))
        row[u_power] = _mpq(coefficient)

    return {degree: list(reversed(row)) for degree, row in parts.items()}, center


def square_root_homogeneous_parts(
    gram_parts: dict[int, list[RationalElement]],
    max_degree: int,
    *,
    progress: bool = False,
) -> list[list[RationalElement]]:
    """Compute homogeneous j_n from sqrt(Q)=sum j_n.

    For the bounded action-angle normalization the finite recurrence is

        j_n = -(1/(2n)) sum_k (2n-3k) q_k j_(n-k).
    """
    result: list[list[RationalElement]] = [[QQ.one]]
    determinant_degree = max(gram_parts)

    for degree in range(1, max_degree + 1):
        accumulator: list[RationalElement] = []
        for k in range(1, min(determinant_degree, degree) + 1):
            qk = gram_parts.get(k)
            if not qk:
                continue
            multiplier = _mpq(2 * degree - 3 * k)
            if multiplier == 0:
                continue
            product = dup_mul(qk, result[degree - k], QQ)
            if multiplier != 1:
                product = [multiplier * coefficient for coefficient in product]
            accumulator = dup_add(accumulator, product, QQ)

        denominator = _mpq(2 * degree)
        result.append(dup_strip([-coefficient / denominator for coefficient in accumulator]))
        if progress and degree % 20 == 0:
            print(f"  density degree {degree}/{max_degree}", flush=True)

    return result


@lru_cache(None)
def angular_moment(cos_power: int, sin_power: int) -> MPQ:
    """(1/pi) integral_0^(2pi) cos^a(phi) sin^b(phi) dphi."""
    if cos_power < 0 or sin_power < 0 or cos_power % 2 or sin_power % 2:
        return QQ.zero
    p = cos_power // 2
    q = sin_power // 2
    return _mpq(sp.Rational(
        2 * math.comb(2 * p, p) * math.comb(2 * q, q),
        4 ** (p + q) * math.comb(p + q, p),
    ))


def period_coefficients(
    family: int | str,
    terms: int,
    *,
    progress: bool = False,
) -> tuple[list[sp.Rational], sp.Expr]:
    """Return b_0,...,b_(terms-1) and det(G_i)(0)."""
    if isinstance(family, str):
        family = FAMILY_INDEX[family]
    if family not in range(3):
        raise ValueError("family must be 0,1,2 or green/yellow/blue")
    if terms < 1:
        raise ValueError("terms must be positive")

    gram_parts, center = rationalized_gram_parts(family)
    max_degree = 2 * (terms - 1)
    start = time.time()
    density_parts = square_root_homogeneous_parts(
        gram_parts, max_degree, progress=progress
    )
    if progress:
        print(f"  density expansion {time.time() - start:.2f}s", flush=True)

    x_scale_squared = _mpq(sp.Rational(4, 27))
    inverse_y_scale_squared = (
        QQ.one
        if family == 0
        else _mpq(sp.Rational(RATIONAL_Y_DENOMINATOR, 3))
    )

    x_powers = [QQ.one]
    y_powers = [QQ.one]
    for _ in range(terms + 2):
        x_powers.append(x_powers[-1] * x_scale_squared)
        y_powers.append(y_powers[-1] * inverse_y_scale_squared)

    monomials: list[list[tuple[int, int, RationalElement]]] = []
    for degree, dense in enumerate(density_parts):
        polynomial_degree = len(dense) - 1
        row: list[tuple[int, int, RationalElement]] = []
        for position, coefficient in enumerate(dense):
            if coefficient == 0:
                continue
            u_power = polynomial_degree - position
            v_power = degree - u_power
            if v_power % 2:
                continue
            row.append((u_power, v_power, coefficient))
        monomials.append(row)

    output: list[sp.Rational] = []
    for coefficient_index in range(terms):
        total = QQ.zero
        for density_degree in range(2 * coefficient_index + 1):
            harmonic_power = 2 * coefficient_index - density_degree
            if harmonic_power == 0:
                radial_factor = _mpq(sp.Rational(1, 2))
            else:
                radial_factor = _mpq(sp.Rational(
                    ((-1) ** harmonic_power)
                    * (coefficient_index + 1)
                    * math.comb(coefficient_index + harmonic_power, harmonic_power - 1),
                    2 * harmonic_power,
                ))

            for u_power, v_power, density_coefficient in monomials[density_degree]:
                x_exponent = (harmonic_power - u_power) // 2
                x_factor = (
                    x_powers[x_exponent]
                    if x_exponent >= 0
                    else QQ.one / x_powers[-x_exponent]
                )
                y_factor = y_powers[v_power // 2]
                moment = angular_moment(u_power + harmonic_power, v_power)
                if moment:
                    total += (
                        density_coefficient
                        * x_factor
                        * y_factor
                        * moment
                        * radial_factor
                    )

        output.append(sp.Rational(QQ.to_sympy(total)))
        if progress and (coefficient_index + 1) % 10 == 0:
            print(f"  coefficient {coefficient_index + 1}/{terms}", flush=True)

    if output[0] != 1:
        raise AssertionError("normalized period must begin with 1")
    return output, center


def required_scale(coefficients: list[sp.Rational]) -> sp.Integer:
    """Smallest observed exponential denominator scale for this prefix."""
    valuations: dict[int, int] = {}
    for k, coefficient in enumerate(coefficients[1:], start=1):
        for prime, exponent in sp.factorint(sp.denom(coefficient)).items():
            valuations[prime] = max(
                valuations.get(prime, 0), (exponent + k - 1) // k
            )
    return sp.prod(prime**exponent for prime, exponent in valuations.items())


def write_csv(path: Path, families: list[str], terms: int, progress: bool) -> None:
    rows = []
    for name in families:
        print(name, terms, flush=True)
        coefficients, center = period_coefficients(name, terms, progress=progress)
        scale = SCALES[name]
        failures = []
        for k, coefficient in enumerate(coefficients):
            scaled = sp.cancel(coefficient * scale**k)
            integral = sp.denom(scaled) == 1
            if not integral:
                failures.append((k, sp.denom(scaled)))
            rows.append({
                "family": name,
                "k": k,
                "period_coefficient": str(coefficient),
                "scale": str(scale),
                "scaled_integer": str(scaled),
                "is_integer": str(integral).lower(),
            })
        print("  center Gram determinant:", center)
        print("  prefix scale:", required_scale(coefficients))
        print("  result:", "PASS" if not failures else failures[0])

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family",
        choices=[*FAMILY_NAMES, "all"],
        default="all",
    )
    parser.add_argument("-n", "--terms", type=int, default=20)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "abel_wick_period_scaled_integers.csv",
    )
    args = parser.parse_args()
    families = list(FAMILY_NAMES) if args.family == "all" else [args.family]
    write_csv(args.out, families, args.terms, args.progress)


if __name__ == "__main__":
    main()
