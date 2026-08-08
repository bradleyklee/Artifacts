#!/usr/bin/env python3
"""Exact setup and bounded certificate search for even sphere quartics.

Requires SymPy.  The code uses Chapter 4's alpha=H convention and the chart
u=Jz^2, v=cos(phi)^2.  It is intentionally separate from the plane alpha=2H
pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence, Tuple
import time
import itertools

import sympy as sp

u, v, y, alpha = sp.symbols("u v y alpha")
X, Y, Z = sp.symbols("X Y Z")
_search_serial = itertools.count()


@dataclass(frozen=True)
class EvenSphereModel:
    name: str
    h_xyz: sp.Expr

    def action_fiber(self) -> sp.Expr:
        return sp.expand(
            self.h_xyz.subs({X: (1-u)*v, Y: (1-u)*(1-v), Z: u}) - alpha
        )


def general_quartic(coefficients: Sequence[sp.Expr], name: str = "general") -> EvenSphereModel:
    """Ten-coefficient degree <=2 polynomial in X,Y,Z."""
    if len(coefficients) != 10:
        raise ValueError("expected [c0,cx,cy,cz,cxx,cyy,czz,cxy,cyz,czx]")
    c0, cx, cy, cz, cxx, cyy, czz, cxy, cyz, czx = coefficients
    H = (c0 + cx*X + cy*Y + cz*Z + cxx*X**2 + cyy*Y**2 + czz*Z**2
         + cxy*X*Y + cyz*Y*Z + czx*Z*X)
    return EvenSphereModel(name, sp.expand(H))


def showcase_models() -> Dict[str, EvenSphereModel]:
    a, b, c = sp.symbols("a b c")
    return {
        "symmetric_top": EvenSphereModel("symmetric_top", a*(X+Y)+c*Z),
        "asymmetric_top": EvenSphereModel("asymmetric_top", a*X+b*Y+c*Z),
        "octahedral": EvenSphereModel("octahedral", 2*(X**2+Y**2+Z**2)),
    }


def relation_g() -> sp.Expr:
    return y**2-u*v*(1-v)


def reduce_on_curve(expr: sp.Expr, F: sp.Expr) -> sp.Expr:
    """Canonical numerator remainder after rational combination and ideal reduction."""
    num, den = sp.fraction(sp.cancel(expr))
    # Lex order makes the quotient finite in y and in u whenever F has u-degree > 0.
    # EX treats alpha, v, model parameters, and nullspace unknowns as
    # coefficient expressions rather than accidentally freezing the domain.
    generators = [sp.Poly(relation_g(), y, u, domain=sp.EX),
                  sp.Poly(F, y, u, domain=sp.EX)]
    _, rem = sp.reduced(sp.Poly(sp.expand(num), y, u, domain=sp.EX),
                        generators, y, u, domain=sp.EX)
    rem = rem.as_expr()
    return sp.cancel(rem/den)


def derivations(F: sp.Expr):
    Fu, Fv = sp.diff(F, u), sp.diff(F, v)
    if Fu == 0:
        raise ValueError("chosen chart is singular: F_u=0")
    ua = 1/Fu
    ya = v*(1-v)/(2*y*Fu)
    uv = -Fv/Fu
    yv = (uv*v*(1-v)+u*(1-2*v))/(2*y)

    def Da(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(sp.diff(expr, alpha)+ua*sp.diff(expr, u)+ya*sp.diff(expr, y))

    def Dv(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(sp.diff(expr, v)+uv*sp.diff(expr, u)+yv*sp.diff(expr, y))

    return Da, Dv


def period_differential(F: sp.Expr) -> sp.Expr:
    return -1/(4*y*sp.diff(F, u))


def derivative_tower(F: sp.Expr, order: int) -> list[sp.Expr]:
    Da, _ = derivations(F)
    tower = [period_differential(F)]
    for _ in range(order):
        tower.append(sp.cancel(Da(tower[-1])))
    return tower


def verify_derivations(F: sp.Expr) -> None:
    Da, Dv = derivations(F)
    assert reduce_on_curve(Da(F), F) == 0
    assert reduce_on_curve(Da(relation_g()), F) == 0
    assert reduce_on_curve(Dv(F), F) == 0
    assert reduce_on_curve(Dv(relation_g()), F) == 0


def verify_operator_exact(F: sp.Expr, operator: Sequence[sp.Expr], primitive: sp.Expr) -> sp.Expr:
    """Return zero iff A(tau)=D_v(primitive) on the complete intersection."""
    _, Dv = derivations(F)
    tower = derivative_tower(F, len(operator)-1)
    residual = sum(a*w for a, w in zip(operator, tower)) - Dv(primitive)
    return sp.factor(reduce_on_curve(residual, F))


def monomials(max_u: int, max_v: int, max_alpha: int) -> Iterable[sp.Expr]:
    for ia in range(max_alpha+1):
        for iu in range(max_u+1):
            for iv in range(max_v+1):
                yield alpha**ia*u**iu*v**iv


def bounded_certificate_matrix(
    F: sp.Expr,
    order: int,
    operator_alpha_degree: int,
    primitive_u_degree: int,
    primitive_v_degree: int,
    primitive_alpha_degree: int,
    chart_denominator: sp.Expr = sp.S.One,
    chart_denominator_power: int = 0,
) -> Tuple[sp.Matrix, list[sp.Symbol], sp.Expr]:
    """Build the exact homogeneous linear system for A(tau)-D_v(Xi)=0.

    This is a bounded search, not yet a theorem about sufficient support.
    """
    _, Dv = derivations(F)
    tower = derivative_tower(F, order)
    # Method-specific names prevent accidental aliasing with model parameters
    # and with the parallel Dihedral reducer in a shared SymPy process.
    serial=next(_search_serial)
    op_unknowns = sp.symbols(
        f"sphere_certificate_{serial}_operator__0:{(order+1)*(operator_alpha_degree+1)}")
    p_basis = list(monomials(primitive_u_degree, primitive_v_degree, primitive_alpha_degree))
    p_unknowns = sp.symbols(
        f"sphere_certificate_{serial}_primitive__0:{len(p_basis)}")
    unknowns = list(op_unknowns)+list(p_unknowns)

    op = []
    at = iter(op_unknowns)
    for _ in range(order+1):
        op.append(sum(next(at)*alpha**j for j in range(operator_alpha_degree+1)))
    P = sum(c*m for c, m in zip(p_unknowns, p_basis))
    Fu = sp.diff(F, u)
    Xi = P/(y**(2*order-1)*Fu**(2*order-1)
           *chart_denominator**chart_denominator_power)
    residual = sum(a*w for a, w in zip(op, tower))-Dv(Xi)
    reduced = reduce_on_curve(residual, F)
    numerator = sp.together(reduced).as_numer_denom()[0]
    poly = sp.Poly(sp.expand(numerator), y, u, v, alpha)
    equations = poly.coeffs()
    matrix, _ = sp.linear_eq_to_matrix(equations, unknowns)
    return matrix, unknowns, Xi


def adaptive_primitive_search(
    F: sp.Expr,
    order: int,
    operator_alpha_degree: int,
    primitive_alpha_degree: int,
    start_v_degree: int = 0,
    max_v_degree: int | None = None,
    time_limit_seconds: float | None = None,
) -> dict:
    """Grow every consecutive v-support shell until an exact relation closes.

    The u numerator degree is not guessed: reduction modulo F permits the
    canonical bound deg_u(P)<deg_u(F).  A finite max_v_degree or time limit is a
    resource boundary only and returns status ``blocked``, never ``no_relation``.
    """
    du = sp.degree(F, u)
    if du is None or du < 1:
        raise ValueError("chosen chart has no finite u quotient")
    max_u = int(du)-1
    history=[]
    started=time.monotonic()
    v_degree=start_v_degree
    while True:
        if max_v_degree is not None and v_degree > max_v_degree:
            return {"status":"blocked", "blocker":"max_v_degree",
                    "history":history, "next_v_degree":v_degree}
        if time_limit_seconds is not None and time.monotonic()-started > time_limit_seconds:
            return {"status":"blocked", "blocker":"time_limit",
                    "history":history, "next_v_degree":v_degree}
        tick=time.monotonic()
        M,unknowns,Xi=bounded_certificate_matrix(
            F,order,operator_alpha_degree,max_u,v_degree,primitive_alpha_degree
        )
        null=M.nullspace()
        relations=[z for z in null
                   if any(z[i] for i in range((order+1)*(operator_alpha_degree+1)))]
        history.append({"v_degree":v_degree,"matrix_shape":list(M.shape),
                        "nullity":len(null),"operator_relations":len(relations),
                        "seconds":time.monotonic()-tick})
        if relations:
            z=relations[0]
            Xi0=sp.factor(Xi.subs(dict(zip(unknowns,list(z)))))
            operator=[]
            width=operator_alpha_degree+1
            for k in range(order+1):
                operator.append(sp.factor(sum(z[width*k+j]*alpha**j
                                              for j in range(width))))
            residual=verify_operator_exact(F,operator,Xi0)
            if residual != 0:
                raise AssertionError("nullspace relation failed exact replay")
            return {"status":"closed", "history":history,
                    "v_degree":v_degree,"operator":operator,
                    "primitive":Xi0,"exact_residual":residual}
        v_degree += 1


def dissertation_asymmetric_operator() -> list[sp.Expr]:
    a, b, c = sp.symbols("a b c")
    s1, s2 = a+b+c, a*b+b*c+c*a
    return [s1-3*alpha,
            -4*(s2-2*alpha*s1+3*alpha**2),
            -4*(alpha-a)*(alpha-b)*(alpha-c)]


def self_check() -> None:
    models = showcase_models()
    for model in models.values():
        F = model.action_fiber()
        verify_derivations(F)
        print(f"DERIVATIONS_PASS {model.name} deg_u={sp.degree(F,u)} deg_v={sp.degree(F,v)}")
    F = models["asymmetric_top"].action_fiber()
    tower = derivative_tower(F, 2)
    assert len(tower) == 3
    print("ASYMMETRIC_TOWER_PASS order=2")


if __name__ == "__main__":
    self_check()
