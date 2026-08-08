#!/usr/bin/env python3
from fractions import Fraction as Q
from math import factorial,prod
import json,argparse
from generic_even_p_quintic import fadd,fmul,monomial_fourier

def components(spec):
 out=[]
 for ds,mons in sorted(spec.items(),key=lambda z:int(z[0])):
  d=int(ds);g={}
  for pe,qe,c in mons:g=fadd(g,monomial_fourier(int(pe),int(qe),Q(c)))
  out.append((d,g))
 return out

def ctprod(a,b):
 if len(a)>len(b):a,b=b,a
 return sum((u*b.get(-k,Q(0)) for k,u in a.items()),Q(0))

def series(spec,N):
 comps=components(spec);assert [d for d,g in comps]==[3,4]
 g3,g4=comps[0][1],comps[1][1]
 p3=[{0:Q(1)}];p4=[{0:Q(1)}]
 for _ in range(2*(N-1)+1):p3.append(fmul(p3[-1],g3))
 for _ in range(N):p4.append(fmul(p4[-1],g4))
 out=[]
 for n in range(N):
  z=Q(0)
  for c in range(n+1):
   a=2*c;b=n-c;m=n+c
   rising=prod(range(n+1,n+1+m)) if m else 1
   z+=Q(((-1)**m)*rising,factorial(a)*factorial(b))*ctprod(p3[a],p4[b])
  out.append(z)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--terms',type=int,default=100);ap.add_argument('--output',required=True)
 ns=ap.parse_args();rec=json.load(open(ns.model));seq=series(rec['monomials'],ns.terms);rec=dict(rec);rec['quantity']='T(alpha)/(2*pi)';rec['terms']=[str(x) for x in seq]
 json.dump(rec,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
if __name__=='__main__':main()
