#!/usr/bin/env python3
"""Independent Chapter-3 DihedralToODE reconstruction for sphere curves.

No original notebook/source implementation is used.  Energy convention:
alpha=H, as in Chapter 4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import time
import itertools

import sympy as sp

lam, alpha = sp.symbols("lambda alpha")
_search_serial=itertools.count()


@dataclass(frozen=True)
class DihedralSphereModel:
    name: str
    h1: sp.Expr
    h2: sp.Expr
    m: int

    @property
    def rho(self):
        return sp.factor(self.h2*sp.diff(self.h1,lam)
                         +(alpha-self.h1)*sp.diff(self.h2,lam))

    @property
    def lambda_dot_squared(self):
        return sp.factor(-self.m**2*(alpha-self.h1-self.h2)
                         *(alpha-self.h1+self.h2))

    @property
    def lambda_ddot(self):
        return sp.factor(sp.diff(self.lambda_dot_squared,lam)/2)

    @property
    def phi_dot(self):
        return sp.cancel(self.rho/self.h2)


def asymmetric_top(a=sp.Integer(1),b=sp.Integer(2),c=sp.Integer(5)):
    a,b,c=map(sp.sympify,(a,b,c))
    h1=(a+b)/2+(c-(a+b)/2)*lam**2
    h2=(a-b)*(1-lam**2)/2
    return DihedralSphereModel("asymmetric_top",sp.expand(h1),sp.expand(h2),2)


def octahedral():
    h1=sp.Rational(3,2)-3*lam**2+sp.Rational(7,2)*lam**4
    h2=sp.Rational(1,2)*(1-lam**2)**2
    return DihedralSphereModel("octahedral",h1,sp.expand(h2),4)


def tetrahedral():
    """Normalized cubic H=3*sqrt(3)*Jx*Jy*Jz after a phase shift.

    With lambda=Jz and phi shifted by pi/4,
    H=h2(lambda)*cos(2*phi).  This deliberately tests a Hamiltonian that is
    not coordinatewise even; no Chapter-4 operator is supplied to derive().
    """
    h2=sp.Rational(3,2)*sp.sqrt(3)*lam*(1-lam**2)
    return DihedralSphereModel("tetrahedral",sp.S.Zero,h2,2)


def coefficient_vector(poly: sp.Expr, degree: int) -> sp.Matrix:
    p=sp.Poly(sp.expand(poly),lam)
    return sp.Matrix([p.coeff_monomial(lam**j) for j in range(degree+1)])


def dissertation_kernel(model: DihedralSphereModel) -> dict:
    """Construct the Chapter-3 G matrix for w=rho*u-s*rho'*v."""
    rho=model.rho; s=model.lambda_dot_squared
    d=int(sp.degree(rho,lam)); Delta=int(sp.degree(s,lam))-1
    du=d+Delta-1; dv=d-1; ambient=2*d+Delta-1
    columns=[]; labels=[]
    for j in range(du+1):
        columns.append(coefficient_vector(rho*lam**j,ambient)); labels.append(("u",j))
    for j in range(dv+1):
        columns.append(coefficient_vector(-s*sp.diff(rho,lam)*lam**j,ambient)); labels.append(("v",j))
    G=sp.Matrix.hstack(*columns)
    if G.rows != G.cols:
        raise AssertionError(f"non-square dissertation kernel {G.shape}")
    det=sp.factor(G.det())
    return {"d":d,"Delta":Delta,"u_degree":du,"v_degree":dv,
            "ambient_degree":ambient,"labels":labels,"G":G,
            "determinant":det,"invertible":det != 0}


def Dalpha(model: DihedralSphereModel, expr: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.diff(expr,alpha)+(model.h2/model.rho)*sp.diff(expr,lam))


def density_tower(model: DihedralSphereModel, order: int) -> list[sp.Expr]:
    f=sp.cancel(model.h2/model.rho)
    q=[f]
    for _ in range(order): q.append(Dalpha(model,q[-1]))
    return [sp.cancel(model.phi_dot*z) for z in q]


def time_derivative_over_lambda_dot(model: DihedralSphereModel, R: sp.Expr) -> sp.Expr:
    """d_t(lambda_dot*R)=lambda_ddot*R+lambda_dot^2*d_lambda R."""
    return sp.cancel(model.lambda_ddot*R+model.lambda_dot_squared*sp.diff(R,lam))


def bounded_certificate_matrix(model: DihedralSphereModel, order: int,
                               operator_alpha_degree: int,
                               numerator_lambda_degree: int,
                               numerator_alpha_degree: int):
    tower=density_tower(model,order)
    width=operator_alpha_degree+1
    serial=next(_search_serial)
    au=sp.symbols(
        f"dihedral_certificate_{serial}_operator__0:{(order+1)*width}")
    op=[sum(au[width*k+j]*alpha**j for j in range(width))
        for k in range(order+1)]
    basis=[alpha**a*lam**j for a in range(numerator_alpha_degree+1)
           for j in range(numerator_lambda_degree+1)]
    pu=sp.symbols(
        f"dihedral_certificate_{serial}_primitive__0:{len(basis)}")
    P=sum(c*z for c,z in zip(pu,basis))
    pole=2*order-1
    R=P/model.rho**pole
    residual=sum(a*x for a,x in zip(op,tower))-time_derivative_over_lambda_dot(model,R)
    num=sp.together(residual).as_numer_denom()[0]
    equations=sp.Poly(sp.expand(num),lam,alpha).coeffs()
    unknowns=list(au)+list(pu)
    M,_=sp.linear_eq_to_matrix(equations,unknowns)
    return M,unknowns,R


def derive(model: DihedralSphereModel, order: int=2,
           operator_alpha_degree: int=3,
           numerator_lambda_degree: int=8,
           numerator_alpha_degree: int=3):
    M,unknowns,R=bounded_certificate_matrix(
        model,order,operator_alpha_degree,numerator_lambda_degree,numerator_alpha_degree
    )
    width=operator_alpha_degree+1
    rel=[]
    for z in M.nullspace():
        if any(z[i] for i in range((order+1)*width)): rel.append(z)
    if not rel:
        return {"status":"incomplete","matrix":M,"unknowns":unknowns}
    z=rel[0]; sub=dict(zip(unknowns,list(z)))
    operator=[sp.factor(sum(z[width*k+j]*alpha**j for j in range(width)))
              for k in range(order+1)]
    R0=sp.factor(R.subs(sub))
    residual=sp.cancel(sum(a*x for a,x in zip(operator,density_tower(model,order)))
                       -time_derivative_over_lambda_dot(model,R0))
    if residual != 0: raise AssertionError("Dihedral certificate replay failed")
    return {"status":"closed","matrix":M,"nullity":len(M.nullspace()),
            "operator":operator,"R":R0,
            "primitive":"lambda_dot*R","exact_residual":residual}


def adaptive_numerator_search(model: DihedralSphereModel, order: int=2,
                              operator_alpha_degree: int=3,
                              numerator_alpha_degree: int=3,
                              start_lambda_degree: int=0,
                              max_lambda_degree: int | None=None,
                              time_limit_seconds: float | None=None):
    """Visit every lambda-numerator degree; finite caps mean blocked only."""
    history=[]; started=time.monotonic(); degree=start_lambda_degree
    while True:
        if max_lambda_degree is not None and degree > max_lambda_degree:
            return {"status":"blocked","blocker":"max_lambda_degree",
                    "next_lambda_degree":degree,"history":history}
        if time_limit_seconds is not None and time.monotonic()-started > time_limit_seconds:
            return {"status":"blocked","blocker":"time_limit",
                    "next_lambda_degree":degree,"history":history}
        tick=time.monotonic()
        M,unknowns,R=bounded_certificate_matrix(
            model,order,operator_alpha_degree,degree,numerator_alpha_degree)
        width=operator_alpha_degree+1
        rel=[z for z in M.nullspace()
             if any(z[i] for i in range((order+1)*width))]
        result={"status":"incomplete","matrix":M,"unknowns":unknowns}
        if rel:
            z=rel[0]; sub=dict(zip(unknowns,list(z)))
            operator=[sp.factor(sum(z[width*k+j]*alpha**j for j in range(width)))
                      for k in range(order+1)]
            R0=sp.factor(R.subs(sub))
            residual=sp.cancel(sum(a*x for a,x in zip(
                operator,density_tower(model,order)))
                -time_derivative_over_lambda_dot(model,R0))
            if residual != 0:
                raise AssertionError("adaptive Dihedral certificate replay failed")
            result={"status":"closed","matrix":M,"nullity":len(M.nullspace()),
                    "operator":operator,"R":R0,"primitive":"lambda_dot*R",
                    "exact_residual":residual}
        history.append({"lambda_degree":degree,"matrix_shape":list(M.shape),
                        "nonzeros":sum(bool(z) for z in M),
                        "density":float(sum(bool(z) for z in M)/(M.rows*M.cols)),
                        "seconds":time.monotonic()-tick,
                        "closed":result["status"]=="closed"})
        if result["status"]=="closed":
            result["history"]=history
            result["lambda_degree"]=degree
            return result
        degree += 1


def self_check():
    for model in [asymmetric_top(),octahedral(),tetrahedral()]:
        k=dissertation_kernel(model)
        print(f"DIHEDRAL_KERNEL {model.name} shape={k['G'].shape} invertible={k['invertible']}")
        print(f"rho={model.rho}")
        print(f"lambda_dot_squared={model.lambda_dot_squared}")


if __name__=="__main__": self_check()
