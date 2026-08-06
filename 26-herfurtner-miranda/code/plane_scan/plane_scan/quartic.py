from __future__ import annotations

from dataclasses import dataclass
import re

import sympy as sp

from .classify import alpha, classify_invariants


@dataclass(frozen=True)
class QuarticParameters:
    """Invariant parameters for L2=q^2-r p^2, L1=sqrt(U)p+sqrt(V)q."""

    r: sp.Rational
    U: sp.Rational
    V: sp.Rational
    mu: sp.Rational

    @classmethod
    def from_values(cls, r: object, U: object, V: object, mu: object) -> "QuarticParameters":
        return cls(*(sp.Rational(value) for value in (r, U, V, mu)))

    def hamiltonian(self) -> str:
        return (
            "p^2 + q^2 + (q^2 - ("
            f"{self.r})*p^2)*(sqrt({self.U})*p + sqrt({self.V})*q) + "
            f"({self.mu})*(q^2 - ({self.r})*p^2)^2"
        )


def invariants(parameters: QuarticParameters) -> tuple[sp.Poly, sp.Poly]:
    """Binary-quartic invariants of the normalization after projection from a node."""
    r, U, V, mu = parameters.r, parameters.U, parameters.V, parameters.mu
    if r == 0 or mu == 0:
        raise ValueError("the nondegenerate two-node quartic class requires r*mu != 0")

    a1 = sp.expand(
        -12 * mu * r**2 - 32 * mu * r - 12 * mu
        + 3 * r**2 * V + 9 * r * U + 9 * r * V + 3 * U
    )
    a2 = sp.expand(16 * mu**2 * r**2)
    b1 = sp.expand(
        -sp.Rational(3, 2) * (
            -24 * mu * r**2 - 40 * mu * r - 24 * mu
            + 9 * r**2 * U + 6 * r**2 * V + 9 * r * U
            + 9 * r * V + 6 * U + 9 * V
        )
    )
    b2 = sp.expand(
        -sp.Rational(3, 2) * r * (
            96 * mu**2 * r**2 + 160 * mu**2 * r + 96 * mu**2
            - 60 * mu * r**2 * V - 36 * mu * r * U - 36 * mu * r * V
            - 60 * mu * U + 9 * r**2 * V**2 - 18 * r * U * V + 9 * U**2
        )
    )
    b3 = sp.expand(-64 * mu**3 * r**3)
    c4 = sp.Poly(1 + a1 * alpha + a2 * alpha**2, alpha, domain=sp.QQ)
    c6 = sp.Poly(1 + b1 * alpha + b2 * alpha**2 + b3 * alpha**3, alpha, domain=sp.QQ)
    return c4, c6


def verify(parameters: QuarticParameters) -> dict[str, object]:
    c4, c6 = invariants(parameters)
    result = classify_invariants(c4, c6)
    result["parameters"] = {key: str(value) for key, value in parameters.__dict__.items()}
    result["hamiltonian_2H"] = parameters.hamiltonian()
    return result


WITNESSES: dict[tuple[str, ...], QuarticParameters] = {
    tuple(sorted(("I3*", "I1", "I1", "I1"))): QuarticParameters.from_values(1, 64, 0, 8),
    tuple(sorted(("I2*", "I2", "I1", "I1"))): QuarticParameters.from_values(4, 1, 64, sp.Rational(45, 4)),
    tuple(sorted(("I2*", "II", "I1", "I1"))): QuarticParameters.from_values(sp.Rational(27, 37), 1, sp.Rational(1813, 3), sp.Rational(4477, 64)),
    tuple(sorted(("I1*", "I3", "I1", "I1"))): QuarticParameters.from_values(-1, 1, 1, 1),
    tuple(sorted(("I1*", "III", "I1", "I1"))): QuarticParameters.from_values(1, 1, 0, sp.Rational(5, 32)),
    tuple(sorted(("I1*", "I2", "I2", "I1"))): QuarticParameters.from_values(4, 0, 0, 1),
    tuple(sorted(("I1*", "I2", "II", "I1"))): QuarticParameters.from_values(1, 1, 0, sp.Rational(9, 32)),
    tuple(sorted(("I1*", "II", "II", "I1"))): QuarticParameters.from_values(sp.Rational(1, 2), sp.Rational(14112, 5329), sp.Rational(7200, 5329), 1),
}


def structural_candidate(target: tuple[str, ...]) -> bool:
    """For r*mu!=0, infinity is I_n* with n>=1."""
    return any(re.fullmatch(r"I[1-9][0-9]*\*", name) is not None for name in target)
