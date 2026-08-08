#!/usr/bin/env python3
from fractions import Fraction as Q
from math import factorial,prod
import argparse,json

ZERO=(Q(0),Q(0)); ONE=(Q(1),Q(0))
def gadd(x,y):return (x[0]+y[0],x[1]+y[1])
def gmul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def gscale(x,c):return (x[0]*c,x[1]*c)
def fadd(a,b):
 z=dict(a)
 for k,v in b.items():
  z[k]=gadd(z.get(k,ZERO),v)
  if z[k]==ZERO:del z[k]
 return z
def fmul(a,b):
 z={}
 for i,u in a.items():
  for j,v in b.items():z[i+j]=gadd(z.get(i+j,ZERO),gmul(u,v))
 return {k:v for k,v in z.items() if v!=ZERO}
def fpow(a,n):
 z={0:ONE};b=a
 while n:
  if n&1:z=fmul(z,b)
  n//=2
  if n:b=fmul(b,b)
 return z
SIN={1:(Q(0),Q(-1,2)),-1:(Q(0),Q(1,2))}
COS={1:(Q(1,2),Q(0)),-1:(Q(1,2),Q(0))}
def monomial_fourier(pe,qe,c):
 z=fmul(fpow(SIN,pe),fpow(COS,qe));return {k:gscale(v,Q(c)) for k,v in z.items()}
def components(spec):
 out=[]
 for ds,mons in sorted(spec.items(),key=lambda z:int(z[0])):
  g={}
  for pe,qe,c in mons:g=fadd(g,monomial_fourier(int(pe),int(qe),c))
  out.append((int(ds),g))
 return out
def ctprod(a,b):
 if len(a)>len(b):a,b=b,a
 z=ZERO
 for k,u in a.items():z=gadd(z,gmul(u,b.get(-k,ZERO)))
 return z
def series(spec,N):
 comps=components(spec);assert [d for d,g in comps]==[3,4]
 g3,g4=comps[0][1],comps[1][1]
 p3=[{0:ONE}];p4=[{0:ONE}]
 for _ in range(2*(N-1)+1):p3.append(fmul(p3[-1],g3))
 for _ in range(N):p4.append(fmul(p4[-1],g4))
 out=[]
 for n in range(N):
  z=ZERO
  for c in range(n+1):
   a=2*c;b=n-c;m=n+c;rising=prod(range(n+1,n+1+m)) if m else 1;coef=Q(((-1)**m)*rising,factorial(a)*factorial(b));z=gadd(z,gscale(ctprod(p3[a],p4[b]),coef))
  if z[1]!=0:raise ValueError(('nonreal coefficient',n,z))
  out.append(z[0])
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--terms',type=int,default=100);ap.add_argument('--output',required=True);ns=ap.parse_args();rec=json.load(open(ns.model));seq=series(rec['monomials'],ns.terms);rec=dict(rec);rec['quantity']='T(alpha)/(2*pi)';rec['terms']=[str(x) for x in seq];json.dump(rec,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
if __name__=='__main__':main()
