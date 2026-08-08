#!/usr/bin/env python3
"""Exact 400-term verification of the square-hexagon operator ladder.

Also gives a rigorous finite exclusion of polynomial-coefficient operators
of degree <= 5 for every identifiable order 1..56, by full-column-rank
calculation over F_1000003. Full rank modulo one good prime implies full rank
over Q for these rational matrices.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb
import json
import sympy as sp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ALPHA = sp.symbols("alpha")
PRIME = 1000003
OPERATOR_FILES = [
    "order4_operator.json",
    "order5_operator_and_relation.json",
    "order6_operator.json",
    "order8_operator_and_relation.json",
    "order12_operator_and_relation.json",
]

def load_alpha_series():
    seq=[]
    for line in (ROOT/"data/integer_period_bfile_400.txt").read_text().splitlines():
        if not line or line.startswith("#"): continue
        n,b=line.split()
        n=int(n); b=int(b)
        assert n==len(seq)
        seq.append(Q(b,8**n))
    return seq

def load_operator(name):
    d=json.loads((ROOT/"exact"/name).read_text())
    ps=[sp.Poly(sp.sympify(s),ALPHA,domain=sp.QQ) for s in d["polynomials"]]
    assert len(ps)==d["order"]+1
    return d,ps

def annihilator_residuals(seq,ps):
    r=len(ps)-1; N=len(seq); out=[]
    for n in range(N-r):
        z=Q(0)
        for j,p in enumerate(ps):
            for (e,),vv in p.terms():
                k=n-e+j
                if n>=e and k>=j and k<N:
                    fall=1
                    for t in range(j): fall*=k-t
                    z += Q(int(vv.p),int(vv.q))*fall*seq[k]
        out.append(z)
    return out

def qmod(x,p=PRIME):
    return (x.numerator%p)*pow(x.denominator%p,-1,p)%p

def falling_mod(k,j,p=PRIME):
    z=1
    for t in range(j): z=z*(k-t)%p
    return z

def degree_matrix_mod(seq,r,d=5,p=PRIME):
    N=len(seq); rows=N-r; cols=(r+1)*(d+1)
    smod=[qmod(x,p) for x in seq]
    A=np.zeros((rows,cols),dtype=np.int64)
    col=0
    for j in range(r+1):
        for e in range(d+1):
            for n in range(e,rows):
                k=n-e+j
                if k<N and k>=j:
                    A[n,col]=falling_mod(k,j,p)*smod[k]%p
            col+=1
    return A

def rank_mod(A,p=PRIME):
    m,n=A.shape; row=0
    for col in range(n):
        nz=np.flatnonzero(A[row:,col])
        if len(nz)==0: continue
        piv=row+int(nz[0])
        if piv!=row: A[[row,piv]]=A[[piv,row]]
        inv=pow(int(A[row,col]),p-2,p)
        A[row,col:]=(A[row,col:]*inv)%p
        if row+1<m:
            factors=A[row+1:,col].copy()
            nzr=np.flatnonzero(factors)
            if len(nzr):
                rr=row+1+nzr
                A[rr,col:]=(A[rr,col:]-factors[nzr,None]*A[row,col:])%p
        row+=1
        if row==m or row==n: break
    return row

def main():
    seq=load_alpha_series()
    assert len(seq)==400
    print("OPERATOR_LADDER_400")
    for name in OPERATOR_FILES:
        d,ps=load_operator(name)
        residuals=annihilator_residuals(seq,ps)
        assert all(x==0 for x in residuals), name
        print(f"order {d['order']:2d}, degree {max(p.degree() for p in ps):2d}: "
              f"{len(residuals)} exact coefficient equations, zero residual")
    print("DEGREE_LE_5_EXCLUSION_MOD_1000003")
    for r in range(1,57):
        A=degree_matrix_mod(seq,r,5)
        rk=rank_mod(A)
        assert rk==A.shape[1], (r,A.shape,rk)
    print("orders 1..56: full column rank; no nonzero operator of degree <= 5")
    print("OPERATOR_LADDER_400_PASS")

if __name__=="__main__":
    main()
