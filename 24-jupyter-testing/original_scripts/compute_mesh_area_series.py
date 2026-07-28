#!/usr/bin/env python3
"""Exact local power series for the true 3-D surface area.

The surface is Sigma_m = G(D_m), where G=F o iota and
D_m = {H(u,v) >= (1-m)/27} inside the standard triangle.

In harmonic coordinates (x,y):
  u = 1/3 + x/3 + y/(3*sqrt(3)),
  v = 1/3 - x/3 + y/(3*sqrt(3)),
  m = x^2+y^2 + 2/(3sqrt(3))*y*(y^2-3x^2).

The normalized area is Psi(m)=A(m)/(pi*J0), J0=||G_x x G_y||(0,0).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import math
import sympy as sp

x, y = sp.symbols('x y', real=True)
sq3 = sp.sqrt(3)


def restricted_map_xy():
    u = sp.Rational(1,3) + x/sp.Integer(3) + y/(3*sq3)
    v = sp.Rational(1,3) - x/sp.Integer(3) + y/(3*sq3)
    d = sp.expand(u-v)
    s = sp.expand(u+v)
    U = sp.factor(-(3*d**2 - 2) * (
        243*d**4*s - 171*d**4 - 324*d**2*s + 156*d**2 + 108*s - 4
    ) / 32)
    V = sp.factor(9*d * (
        81*d**4*s - 57*d**4 - 108*d**2*s + 52*d**2 + 36*s - 4
    ) / 16)
    W = sp.factor(-d*(27*d**2*s - 19*d**2 - 8) / 4)
    return sp.expand(U), sp.expand(V), sp.expand(W)


def homogeneous_parts(expr: sp.Expr, max_degree: int):
    poly = sp.Poly(sp.expand(expr), x, y)
    parts = [sp.Integer(0) for _ in range(max_degree+1)]
    for (a,b), coeff in poly.terms():
        d = a+b
        if d <= max_degree:
            parts[d] += coeff*x**a*y**b
    return [sp.expand(p) for p in parts]


def sqrt_homogeneous_series(qnorm: sp.Expr, max_degree: int):
    """Return j[0..D] with (sum j_n)^2=qnorm mod degree>D."""
    q = homogeneous_parts(qnorm, max_degree)
    assert sp.simplify(q[0]-1) == 0
    j = [sp.Integer(1)] + [sp.Integer(0)]*max_degree
    for n in range(1,max_degree+1):
        cross = sp.Integer(0)
        for i in range(1,n):
            cross += j[i]*j[n-i]
        j[n] = sp.expand((q[n]-cross)/2)
    return j


def rho_coeffs(max_n: int):
    """rho(z)^2-z rho(z)^3=1, rho(0)=1."""
    z = sp.symbols('z')
    coeffs = [sp.Integer(1)]
    for n in range(1,max_n+1):
        c = sp.symbols(f'c{n}')
        rho = sum(coeffs[k]*z**k for k in range(n)) + c*z**n
        eq = sp.expand(rho**2-z*rho**3-1).coeff(z,n)
        sol = sp.solve(sp.Eq(eq,0), c)[0]
        coeffs.append(sp.factor(sol))
    return coeffs


def series_mul(a,b,N):
    out=[sp.Integer(0)]*(N+1)
    for i,ai in enumerate(a):
        if ai==0: continue
        for j,bj in enumerate(b):
            if i+j>N: break
            if bj!=0: out[i+j]+=ai*bj
    return [sp.factor(v) for v in out]


def series_pow(base,k,N):
    out=[sp.Integer(1)]+[sp.Integer(0)]*N
    cur=base[:]
    e=k
    while e:
        if e&1: out=series_mul(out,cur,N)
        e//=2
        if e: cur=series_mul(cur,cur,N)
    return out


@lru_cache(None)
def trig_integral_over_pi(a:int,b:int,n:int):
    """(1/pi)∫ cos^a theta sin^b theta sin(3theta)^n dtheta."""
    total=sp.Rational(0)
    # sin(3theta)^n = sin^n(theta)*(3-4 sin^2(theta))^n
    for j in range(n+1):
        coeff=sp.binomial(n,j)*sp.Integer(3)**(n-j)*sp.Integer(-4)**j
        A=a
        B=b+n+2*j
        if A%2 or B%2:
            continue
        p=A//2; q=B//2
        # integral/pi = 2*(2p)!(2q)!/[4^(p+q)p!q!(p+q)!]
        val=sp.Rational(2)*sp.factorial(2*p)*sp.factorial(2*q) / (
            sp.Integer(4)**(p+q)*sp.factorial(p)*sp.factorial(q)*sp.factorial(p+q)
        )
        total += coeff*val
    return sp.factor(total)


def compute(N:int):
    U,V,W=restricted_map_xy()
    Gx=sp.Matrix([sp.diff(U,x),sp.diff(V,x),sp.diff(W,x)])
    Gy=sp.Matrix([sp.diff(U,y),sp.diff(V,y),sp.diff(W,y)])
    cross=sp.simplify(Gx.cross(Gy))
    q=sp.expand(cross.dot(cross))
    q0=sp.simplify(q.subs({x:0,y:0}))
    J0=sp.sqrt(q0)
    qnorm=sp.expand(q/q0)

    maxdeg=2*N-2
    jparts=sqrt_homogeneous_series(qnorm,maxdeg)
    jexpr=sp.expand(sum(jparts))
    jpoly=sp.Poly(jexpr,x,y)

    rho=rho_coeffs(2*N)
    lam=sp.Rational(2,3)/sq3
    # Cache rho^k coefficient lists.
    rho_powers={}
    for k in range(2,2*N+1):
        rho_powers[k]=series_pow(rho,k,2*N)

    coeff_m=[sp.Integer(0)]*(N+1)
    for (a,b),c in jpoly.terms():
        d=a+b
        if d>maxdeg: continue
        k=d+2
        maxn=2*N-k
        if maxn<0: continue
        rp=rho_powers[k]
        for n in range(maxn+1):
            total_t=k+n
            if total_t%2: continue
            ell=total_t//2
            if ell<1 or ell>N: continue
            ang=trig_integral_over_pi(a,b,n)
            if ang==0: continue
            term=c*rp[n]*lam**n*ang/sp.Integer(k)
            coeff_m[ell]+=term

    coeff_m=[sp.factor(sp.simplify(c)) for c in coeff_m]
    assert coeff_m[0]==0 and coeff_m[1]==1
    return {
        'U':U,'V':V,'W':W,'cross':cross,'q0':q0,'J0':J0,
        'coeffs':coeff_m,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('-n','--terms',type=int,default=15)
    args=ap.parse_args()
    data=compute(args.terms)
    print('J0^2 =',data['q0'])
    print('J0 =',data['J0'])
    for n,c in enumerate(data['coeffs'][1:],start=1):
        print(n,c)

if __name__=='__main__':
    main()
