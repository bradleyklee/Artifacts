#!/usr/bin/env python3
"""Exact local hypergeometric reduction for the image-area integral.

For N terms, truncate the normalized stretching density J(x,y)/J(0,0)
through total degree 2N-2.  The resulting polynomial area integral over the
cubic region D_m reduces exactly to

    Psi_N(m) = A_N(m) F3(m) + B_N(m) S3(m),

where F3=2F1(1/3,2/3;1;m), S3=m*2F1(1/3,2/3;2;m), and
Psi-Psi_N=O(m^(N+1)).
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sympy as sp

from compute_mesh_area_series import (
    x, y, sq3, restricted_map_xy, sqrt_homogeneous_series, compute
)

u, v, m = sp.symbols("u v m")
H = u*v*(1-u-v)
Hu, Hv = sp.diff(H,u), sp.diff(H,v)
basis = [v, v**2, u*v, u*v**2]


def monomials_leq(total_degree: int):
    return [u**i*v**(d-i) for d in range(total_degree+1) for i in range(d+1)]


def reduce_form(P: sp.Expr, Q: sp.Expr):
    degree = max(sp.Poly(P,u,v).total_degree() if P else 0,
                 sp.Poly(Q,u,v).total_degree() if Q else 0)
    S_mons = monomials_leq(degree+1)
    T_mons = monomials_leq(max(degree-2,0))
    S_vars = sp.symbols(f"S0:{len(S_mons)}")
    T_vars = sp.symbols(f"T0:{len(T_mons)}")

    coeff_info=[]; coeff_vars=[]
    for i,beta in enumerate(basis):
        beta_degree=sp.Poly(beta,u,v).total_degree()
        for power in range(max((degree-beta_degree)//3,0)+1):
            c=sp.symbols(f"c{i}_{power}")
            coeff_info.append((i,power,c)); coeff_vars.append(c)

    S=sum(c*z for c,z in zip(S_vars,S_mons))
    T=sum(c*z for c,z in zip(T_vars,T_mons))
    reduced_P=sum(c*H**power*basis[i] for i,power,c in coeff_info)
    residual_P=sp.expand(sp.diff(S,u)+T*Hu+reduced_P-P)
    residual_Q=sp.expand(sp.diff(S,v)+T*Hv-Q)
    pp=sp.Poly(residual_P,u,v); pq=sp.Poly(residual_Q,u,v)
    monomials=set(pp.monoms()) | set(pq.monoms())
    equations=[]
    for mon in monomials:
        a=pp.coeff_monomial(mon); b=pq.coeff_monomial(mon)
        if a: equations.append(a)
        if b: equations.append(b)
    unknowns=list(S_vars)+list(T_vars)+coeff_vars
    matrix,rhs=sp.linear_eq_to_matrix(equations,unknowns)
    solution=next(iter(sp.linsolve((matrix,rhs),unknowns)))
    free=set().union(*(z.free_symbols for z in solution))
    gauge={z:0 for z in free if z not in coeff_vars}
    solution=[sp.simplify(z.subs(gauge)) for z in solution]
    sol=dict(zip(unknowns,solution))
    return {(i,p):sp.factor(sol[c]) for i,p,c in coeff_info}


def derive(N: int):
    U,V,W=restricted_map_xy()
    Gx=sp.Matrix([sp.diff(U,x),sp.diff(V,x),sp.diff(W,x)])
    Gy=sp.Matrix([sp.diff(U,y),sp.diff(V,y),sp.diff(W,y)])
    cross=Gx.cross(Gy)
    q=sp.expand(cross.dot(cross))
    q0=sp.simplify(q.subs({x:0,y:0}))
    jparts=sqrt_homogeneous_series(sp.expand(q/q0),2*N-2)
    jxy=sp.expand(sum(jparts))

    xuv=sp.Rational(3,2)*(u-v)
    yuv=sq3*sp.Rational(1,2)*(3*u+3*v-2)
    rho=sp.expand(sp.Rational(27,2)/sq3*jxy.subs({x:xuv,y:yuv}))
    Q=sp.Integer(0)
    for (a,b),c in sp.Poly(rho,u,v).terms():
        Q += c*u**(a+1)*v**b/sp.Integer(a+1)

    coeffs=reduce_form(sp.Integer(0),sp.expand(Q))
    h=(1-m)/27
    F,S=sp.symbols("F3 S3")
    I1=-sp.Rational(2,27)*S
    I2=sp.Rational(2,3)*I1
    I3=sp.Rational(1,3)*I1
    I4=-(sp.Rational(1,81)*m*(1-m)*F+sp.Rational(1,243)*(1+2*m)*S)
    expr=sp.Integer(0)
    for i,I in enumerate([I1,I2,I3,I4]):
        p=sum(value*h**power for (j,power),value in coeffs.items() if j==i)
        expr += sq3*p*I
    expr=sp.expand(expr)
    A=sp.factor(expr.coeff(F))
    B=sp.factor(expr.coeff(S))
    return A,B,compute(N)["coeffs"]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("-n","--terms",type=int,default=8)
    ap.add_argument("--out",type=Path,
                    default=Path(__file__).resolve().parents[1]/"data"/
                    "image_area_hypergeometric_reduction_N8.txt")
    args=ap.parse_args()
    A,B,coeffs=derive(args.terms)
    lines=[
        f"IMAGE-AREA HYPERGEOMETRIC REDUCTION THROUGH m^{args.terms}",
        "",
        "F3(m) = 2F1(1/3,2/3;1;m)",
        "S3(m) = m*2F1(1/3,2/3;2;m)",
        f"Psi_{args.terms}(m) = A_{args.terms}(m)*F3(m) + B_{args.terms}(m)*S3(m)",
        f"Psi(m)-Psi_{args.terms}(m) = O(m^{args.terms+1})",
        "",
        f"A_{args.terms}(m) = {A}",
        "",
        f"B_{args.terms}(m) = {B}",
        "",
        "Checked coefficients:",
    ]
    lines += [f"c_{i} = {coeffs[i]}" for i in range(1,args.terms+1)]
    args.out.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(args.out)

if __name__ == "__main__":
    main()
