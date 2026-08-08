#!/usr/bin/env python3
"""Exact small-oval period series by Fourier-valued series reversion."""
from fractions import Fraction as Q

def fadd(a,b):
    z=dict(a)
    for k,v in b.items():
        z[k]=z.get(k,Q(0))+v
        if not z[k]: del z[k]
    return z
def fscale(a,q): return {k:q*v for k,v in a.items() if q*v}
def fmul(a,b):
    z={}
    for i,u in a.items():
        for j,v in b.items(): z=fadd(z,{i+j:u*v})
    return z
def spow(L,p,nmax):
    out=[{} for _ in range(nmax+1)]; out[0]={0:Q(1)}
    for _ in range(p):
        nxt=[{} for _ in range(nmax+1)]
        for i in range(nmax+1):
            for j in range(nmax+1-i):
                if out[i] and L[j]: nxt[i+j]=fadd(nxt[i+j],fmul(out[i],L[j]))
        out=nxt
    return out
def angular(m): return {0:Q(1)} if m==0 else {m:Q(1,2),-m:Q(1,2)}
def period_coeffs(spec,N=10):
    L=[{} for _ in range(N+2)]; L[1]={0:Q(1,2)}
    for n in range(2,N+2):
        nonlinear={}
        for r,ms in spec.items():
            pw=spow(L,r+1,n)
            for m,q in ms.items():
                nonlinear=fadd(nonlinear,fscale(fmul(pw[n],angular(m)),Q(q)))
        L[n]=fscale(nonlinear,Q(-1,2))
    # T/(2*pi) = 2*d_alpha CT(lambda)
    return [2*Q(k+1)*L[k+1].get(0,Q(0)) for k in range(N+1)]

if __name__=="__main__":
    from portfolio_univariate_sweep import CASES
    for name,spec in CASES.items():
        q=period_coeffs(spec,10)
        print(name, ", ".join(map(str,q)))
