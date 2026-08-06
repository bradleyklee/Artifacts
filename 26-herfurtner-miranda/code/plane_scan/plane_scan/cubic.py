from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .classify import alpha, classify_invariants


@dataclass(frozen=True)
class CubicParameters:
    a: sp.Rational
    b: sp.Rational
    c: sp.Rational
    d: sp.Rational

    @classmethod
    def from_values(cls, a: int, b: int, c: int, d: int) -> "CubicParameters":
        return cls(*(sp.Rational(value) for value in (a, b, c, d)))

    def hamiltonian(self) -> str:
        return (
            "p^2 + q^2 + "
            f"({self.a})*p^3 + ({self.b})*p^2*q + "
            f"({self.c})*p*q^2 + ({self.d})*q^3"
        )


def invariants(parameters: CubicParameters) -> tuple[sp.Poly, sp.Poly, dict[str, sp.Expr]]:
    """Aronhold invariants specialized to alpha=p^2+q^2+homogeneous cubic.

    The normalization is chosen so c4(0)=c6(0)=1 and Delta=c4^3-c6^2.
    """
    a, b, c, d = parameters.a, parameters.b, parameters.c, parameters.d
    k = sp.expand(9 * a * c - 3 * b**2 + 9 * b * d - 3 * c**2)
    m = sp.expand(
        -108 * a**2 + 108 * a * c - 72 * b**2 + 108 * b * d
        - 72 * c**2 - 108 * d**2
    )
    ell = sp.expand(
        729 * a**2 * d**2 - 486 * a * b * c * d + 108 * a * c**3
        + 108 * b**3 * d - 27 * b**2 * c**2
    )
    c4 = sp.Poly(1 - k * alpha, alpha, domain=sp.QQ)
    c6 = sp.Poly(1 + sp.Rational(1, 8) * m * alpha + sp.Rational(1, 8) * ell * alpha**2, alpha, domain=sp.QQ)
    return c4, c6, {"K": k, "M": m, "L": ell}


def verify(parameters: CubicParameters) -> dict[str, object]:
    c4, c6, reduced = invariants(parameters)
    result = classify_invariants(c4, c6)
    result["parameters"] = {key: str(value) for key, value in parameters.__dict__.items()}
    result["reduced_parameters"] = {key: str(value) for key, value in reduced.items()}
    result["hamiltonian_2H"] = parameters.hamiltonian()
    return result


WITNESSES: dict[tuple[str, ...], CubicParameters] = {
    tuple(sorted(("III*", "I1", "I1", "I1"))): CubicParameters.from_values(0, 0, 1, 1),
    tuple(sorted(("IV*", "I2", "I1", "I1"))): CubicParameters.from_values(1, 0, 0, 1),
    tuple(sorted(("IV*", "II", "I1", "I1"))): CubicParameters.from_values(-1, -3, 0, -2),
}


def structural_candidate(target: tuple[str, ...]) -> bool:
    """At infinity this class can only have IV*, III*, or II*."""
    return any(name in target for name in ("IV*", "III*", "II*"))
