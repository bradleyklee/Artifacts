#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction as Q
from math import factorial, prod
import json, argparse

# Fourier polynomials in z=e^{i phi}; coefficients rational because p exponent is even.
def fadd(a,b):
    z=dict(a)
    for k,v in b.items():
        z[k]=z.get(k,Q(0))+v
        if not z[k]: del z[k]
    return z

def fscale(a,c): return {k:c*v for k,v in a.items() if c*v}

def fmul(a,b):
    z={}
    for i,u in a.items():
        for j,v in b.items(): z[j+i]=z.get(j+i,Q(0))+u*v
    return {k:v for k,v in z.items() if v}

def fpow(a,n):
    z={0:Q(1)}
    b=a
    while n:
        if n&1:z=fmul(z,b)
        n//=2
        if n:b=fmul(b,b)
    return z

def monomial_fourier(p_exp,q_exp,coeff=Q(1)):
    # p=r sin(phi), q=r cos(phi); only even p_exp supported rationally.
    if p_exp%2: raise ValueError('p exponent must be even')
    sin={1:Q(1,2),-1:Q(-1,2)} # omit 1/i; correct below by (-1)^(p/2)
    cos={1:Q(1,2),-1:Q(1,2)}
    z=fmul(fpow(sin,p_exp),fpow(cos,q_exp))
    return fscale(z, coeff*((-1)**(p_exp//2)))

def weighted_compositions(target,weights):
    out=[]
    def rec(i,left,row):
        if i==len(weights):
            if left==0: out.append(tuple(row))
            return
        w=weights[i]
        for k in range(left//w+1): rec(i+1,left-k*w,row+[k])
    rec(0,target,[])
    return out

def period_coefficients(components,N):
    # components: list (degree, Fourier angular polynomial f_d)
    weights=[d-2 for d,_ in components]
    maxks=[2*(N-1)//w for w in weights]
    powers=[]
    for (_,g),mx in zip(components,maxks):
        arr=[{0:Q(1)}]
        for _ in range(mx): arr.append(fmul(arr[-1],g))
        powers.append(arr)
    out=[]
    for n in range(N):
        z=Q(0)
        for ks in weighted_compositions(2*n,weights):
            m=sum(ks)
            rising=prod(range(n+1,n+1+m)) if m else 1
            coeff=Q(((-1)**m)*rising,prod(factorial(k) for k in ks))
            four={0:Q(1)}
            for arr,k in zip(powers,ks): four=fmul(four,arr[k])
            z += coeff*four.get(0,Q(0))
        out.append(z)
    return out

# E=p^2+q^2 + q^3-2p^2q + 1/2 p^4+p^2q^2-1/3 q^4 + p^2q^3+2/5 q^5.
COMPONENT_MONOMIALS={
  3:[(0,3,Q(1)),(2,1,Q(-2))],
  4:[(4,0,Q(1,2)),(2,2,Q(1)),(0,4,Q(-1,3))],
  5:[(2,3,Q(1)),(0,5,Q(2,5))],
}

def components():
    out=[]
    for d,mons in sorted(COMPONENT_MONOMIALS.items()):
        g={}
        for pe,qe,c in mons:g=fadd(g,monomial_fourier(pe,qe,c))
        out.append((d,g))
    return out

def energy_sparse():
    E={(0,2,0):Q(1),(0,0,2):Q(1)}
    for d,mons in COMPONENT_MONOMIALS.items():
        for pe,qe,c in mons:E[(0,pe,qe)]=E.get((0,pe,qe),Q(0))+c
    return E

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--terms',type=int,default=80);ap.add_argument('--output')
    ns=ap.parse_args(); seq=period_coefficients(components(),ns.terms)
    rec={
      'example_id':'weird_quintic_p_even',
      'E':'p**2+q**2+q**3-2*p**2*q+p**4/2+p**2*q**2-q**4/3+p**2*q**3+2*q**5/5',
      'symmetry':'E(-p,q)=E(p,q); no q-reflection assumed',
      'quantity':'T(alpha)/(2*pi)',
      'terms':[str(x) for x in seq]
    }
    txt=json.dumps(rec,indent=2)+'\n'
    if ns.output:open(ns.output,'w').write(txt)
    else:print(txt)
if __name__=='__main__':main()
