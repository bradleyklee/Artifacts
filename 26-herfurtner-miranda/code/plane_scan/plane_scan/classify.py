from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import sympy as sp

from .kodaira import fiber_from_valuations

alpha = sp.symbols("alpha")


@dataclass(frozen=True)
class LocalFiber:
    location_factor: str
    factor_degree: int
    fiber: str
    v_c4: int
    v_c6: int
    v_delta: int


def polynomial_valuation(poly: sp.Poly, factor: sp.Poly) -> int:
    """Return the exact exponent of factor in poly by repeated exact division."""
    value = 0
    remainder_poly = poly
    while True:
        quotient, remainder = sp.div(remainder_poly, factor)
        if not remainder.is_zero:
            return value
        value += 1
        remainder_poly = quotient


def canonical_fibers(fibers: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(fibers))


def classify_invariants(c4: sp.Poly, c6: sp.Poly) -> dict[str, object]:
    """Factor Delta=c4^3-c6^2 and classify every finite point and infinity."""
    delta = sp.Poly(sp.expand(c4.as_expr() ** 3 - c6.as_expr() ** 2), alpha, domain=sp.QQ)
    if delta.is_zero:
        raise ValueError("identically zero discriminant")

    finite: list[LocalFiber] = []
    fibers: list[str] = []
    _, factors = sp.factor_list(delta.as_expr(), alpha)
    for factor_expr, delta_order in factors:
        factor = sp.Poly(factor_expr, alpha, domain=sp.QQ)
        v_c4 = polynomial_valuation(c4, factor)
        v_c6 = polynomial_valuation(c6, factor)
        fiber = fiber_from_valuations(v_c4, v_c6, delta_order)
        factor_degree = factor.degree()
        fibers.extend([fiber] * factor_degree)
        finite.append(
            LocalFiber(
                location_factor=sp.sstr(sp.factor(factor_expr)),
                factor_degree=factor_degree,
                fiber=fiber,
                v_c4=v_c4,
                v_c6=v_c6,
                v_delta=delta_order,
            )
        )

    v_c4_inf = 4 - c4.degree()
    v_c6_inf = 6 - c6.degree()
    v_delta_inf = 12 - delta.degree()
    while v_c4_inf >= 4 and v_c6_inf >= 6 and v_delta_inf >= 12:
        v_c4_inf -= 4
        v_c6_inf -= 6
        v_delta_inf -= 12
    infinity_fiber = fiber_from_valuations(v_c4_inf, v_c6_inf, v_delta_inf)
    fibers.append(infinity_fiber)

    return {
        "fibers": list(canonical_fibers(fibers)),
        "c4": sp.sstr(sp.factor(c4.as_expr())),
        "c6": sp.sstr(sp.factor(c6.as_expr())),
        "delta": sp.sstr(sp.factor(delta.as_expr())),
        "finite": [asdict(item) for item in finite],
        "infinity": {
            "fiber": infinity_fiber,
            "v_c4": v_c4_inf,
            "v_c6": v_c6_inf,
            "v_delta": v_delta_inf,
        },
        "euler_total": sum(_euler_number(name) for name in fibers),
    }


def _euler_number(name: str) -> int:
    fixed = {"II": 2, "III": 3, "IV": 4, "I0*": 6, "IV*": 8, "III*": 9, "II*": 10}
    if name in fixed:
        return fixed[name]
    if name.startswith("I") and name.endswith("*"):
        return int(name[1:-1]) + 6
    if name.startswith("I"):
        return int(name[1:])
    raise ValueError(name)
