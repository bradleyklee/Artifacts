#!/usr/bin/env python3
"""Octahedral invariant chart, independent of the DihedralToODE certificate.

The reflection v -> 1-v suggests t=v(1-v).  With w^2=u*t*(1-4t),
the period form is -dt/(4*w*H_u).  This removes the redundant angular double
cover before reductive nullspace calculations.
"""
from __future__ import annotations

import sympy as sp

u, t, w, alpha = sp.symbols("u t w alpha")
F = 4*(1-t)*u**2 + 4*(2*t-1)*u + 2-4*t-alpha
G = w**2-u*t*(1-4*t)


def reduce_curve(expr: sp.Expr) -> sp.Expr:
    num, den = sp.fraction(sp.cancel(expr))
    gens = [sp.Poly(G,w,u,domain=sp.EX), sp.Poly(F,w,u,domain=sp.EX)]
    _, rem = sp.reduced(sp.Poly(sp.expand(num),w,u,domain=sp.EX),
                        gens,w,u,domain=sp.EX)
    return sp.cancel(rem.as_expr()/den)


Fu, Ft = sp.diff(F,u), sp.diff(F,t)
ua = 1/Fu
wa = t*(1-4*t)/(2*w*Fu)
ut = -Ft/Fu
wt = (ut*t*(1-4*t)+u*(1-8*t))/(2*w)


def Da(expr: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.diff(expr,alpha)+ua*sp.diff(expr,u)+wa*sp.diff(expr,w))


def Dt(expr: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.diff(expr,t)+ut*sp.diff(expr,u)+wt*sp.diff(expr,w))


def tower(order: int) -> list[sp.Expr]:
    out=[-1/(4*w*Fu)]
    for _ in range(order): out.append(Da(out[-1]))
    return out


def known_operator() -> list[sp.Expr]:
    return [9*(6-5*alpha),
            -16*(12-22*alpha+9*alpha**2),
            16*(2-3*alpha)*(1-alpha)*(2-alpha)]


def bounded_matrix(max_u: int, max_t: int, max_alpha: int,
                   q_power: int = 0):
    order=2; W=tower(order)
    au=sp.symbols("a0:12")
    op=[sum(au[4*k+j]*alpha**j for j in range(4)) for k in range(3)]
    basis=[alpha**a*u**i*t**j for a in range(max_alpha+1)
           for i in range(max_u+1) for j in range(max_t+1)]
    pu=sp.symbols(f"p0:{len(basis)}")
    P=sum(c*m for c,m in zip(pu,basis))
    Xi=P/(w**3*Fu**3*(1-t)**q_power)
    residual=sum(a*z for a,z in zip(op,W))-Dt(Xi)
    num=sp.together(reduce_curve(residual)).as_numer_denom()[0]
    eq=sp.Poly(sp.expand(num),w,u,t,alpha).coeffs()
    unknowns=list(au)+list(pu)
    M,_=sp.linear_eq_to_matrix(eq,unknowns)
    return M,unknowns,Xi


def verify(operator, primitive):
    residual=sum(a*z for a,z in zip(operator,tower(len(operator)-1)))-Dt(primitive)
    return sp.factor(reduce_curve(residual))


if __name__ == "__main__":
    assert reduce_curve(Da(F)) == 0 and reduce_curve(Da(G)) == 0
    assert reduce_curve(Dt(F)) == 0 and reduce_curve(Dt(G)) == 0
    print("OCTAHEDRAL_INVARIANT_DERIVATIONS_PASS")
    print(f"F={F}")
    print(f"G={G}")
