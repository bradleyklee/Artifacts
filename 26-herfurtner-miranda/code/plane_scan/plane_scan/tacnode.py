from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .classify import alpha, classify_invariants


@dataclass(frozen=True)
class TacnodeParameters:
    """Harmonic quartic with a fixed tacnode at [1:0:0]."""

    s: sp.Rational
    v: sp.Rational
    w: sp.Rational
    c: sp.Rational

    @classmethod
    def from_values(cls, s: object, v: object, w: object, c: object) -> "TacnodeParameters":
        return cls(*(sp.Rational(value) for value in (s, v, w, c)))

    @property
    def A(self) -> sp.Rational:
        return sp.expand(self.v**2 - 4 * self.c)

    def hamiltonian(self) -> str:
        s, v, w, c = self.s, self.v, self.w, self.c
        return (
            "p^2 + q^2 + "
            f"({2*s})*p^2*q + ({v})*p*q^2 + ({w})*q^3 + "
            f"({s**2})*p^2*q^2 + ({s*v})*p*q^3 + ({c})*q^4"
        )


def invariants(parameters: TacnodeParameters) -> tuple[sp.Poly, sp.Poly]:
    """Normalized binary-quartic invariants after projection from the tacnode.

    The residual double cover is
      Y^2 = (v^2-4c)x^4 - 4w x^3 - 4x^2 + 4 alpha.
    With I/16 and J/128 normalization this gives c4 and c6 below.
    """
    A, w = parameters.A, parameters.w
    c4 = sp.Poly(1 + 3 * A * alpha, alpha, domain=sp.QQ)
    c6 = sp.Poly(1 - (9 * A + sp.Rational(27, 2) * w**2) * alpha, alpha, domain=sp.QQ)
    return c4, c6


def local_tacnode_check(parameters: TacnodeParameters) -> dict[str, str]:
    """Return the exact local conditions at [1:0:0]."""
    s, v, w, c = parameters.s, parameters.v, parameters.w, parameters.c
    return {
        "quadratic_cone": sp.sstr((sp.Symbol("z") + s * sp.Symbol("x")) ** 2),
        "cubic_restriction_on_tangent": "0",
        "quartic_restriction_on_tangent": sp.sstr(sp.factor(c - s * w + s**2 - alpha * s**4)),
        "generic_type": "A3 tacnode when the quartic restriction is nonzero",
    }


def verify(parameters: TacnodeParameters) -> dict[str, object]:
    c4, c6 = invariants(parameters)
    result = classify_invariants(c4, c6)
    result["parameters"] = {key: str(value) for key, value in parameters.__dict__.items()}
    result["A"] = str(parameters.A)
    result["hamiltonian_2H"] = parameters.hamiltonian()
    result["local_check"] = local_tacnode_check(parameters)
    result["projected_quartic"] = (
        f"({parameters.A})*x^4 - ({4*parameters.w})*x^3 - 4*x^2 + 4*E"
    )
    result["normalized_time_form"] = f"dx/((1+({parameters.s})*x)*sqrt(Q))"
    result["time_form_type"] = "holomorphic" if parameters.s == 0 else "meromorphic_third_kind"
    result["period_form_warning"] = (
        "For s nonzero the extra factor 1/(1+s*x) makes the Hamiltonian time form "
        "meromorphic, so its period need not satisfy the order-two holomorphic elliptic equation."
    )
    return result


HOLOMORPHIC_EXAMPLE = TacnodeParameters.from_values(0, 0, 1, sp.Rational(-1, 4))
MEROMORPHIC_EXAMPLE = TacnodeParameters.from_values(1, 0, 1, sp.Rational(-1, 4))
EXAMPLE = HOLOMORPHIC_EXAMPLE
