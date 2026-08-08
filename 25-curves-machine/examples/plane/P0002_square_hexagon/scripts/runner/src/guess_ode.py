#!/usr/bin/env python3
"""Guess polynomial-coefficient ODEs from exact ordinary power series."""
from fractions import Fraction as Q
from exp_to_ode_certificate import nullspace

def falling(n,j):
    z=1
    for k in range(j):z*=n-k
    return z
def guess(seq,max_order=6,max_degree=14,holdout=6):
  N=len(seq)
  for r in range(1,max_order+1):
    for d in range(max_degree+1):
      u=(r+1)*(d+1);train=N-holdout
      if train<u+2:continue
      cols=[];labs=[]
      for j in range(r+1):
        for e in range(d+1):
          col={}
          for n in range(train):
            k=n-e+j
            if n>=e and 0<=k<N and k>=j:col[(0,n)]=Q(falling(k,j))*seq[k]
          cols.append(col);labs.append((j,e))
      basis,_,_=nullspace(cols)
      for x in basis:
        if not any(x):continue
        def ck(n):
          return sum(x[t]*Q(falling(n-e+j,j))*seq[n-e+j]
                     for t,(j,e) in enumerate(labs) if n>=e and 0<=n-e+j<N and n-e+j>=j)==0
        if all(ck(n) for n in range(train,N-r)):
          pivot=max(i for i,z in enumerate(x) if z);x=[z/x[pivot] for z in x]
          ps=[{} for _ in range(r+1)]
          for z,(j,e) in zip(x,labs):
            if z:ps[j][e]=z
          return r,d,ps
  return None
def pstr(p):return ' + '.join(f'({v})*alpha^{e}' for e,v in sorted(p.items())).replace('+ (-','- (') or '0'
if __name__=='__main__':
 import json,sys
 data=json.load(open(sys.argv[1]));seq=[Q(x) for x in data[sys.argv[2]]['terms']]
 ans=guess(seq)
 print(None if ans is None else (ans[0],ans[1]))
 if ans:
  for j,p in enumerate(ans[2]):print('p'+str(j),'=',pstr(p))
