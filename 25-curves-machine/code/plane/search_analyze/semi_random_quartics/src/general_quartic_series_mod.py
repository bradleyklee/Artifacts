#!/usr/bin/env python3
import argparse,json,time
from math import factorial
import sympy as sp

def fadd(a,b,p):
 z=dict(a)
 for k,v in b.items():
  z[k]=(z.get(k,0)+v)%p
  if z[k]==0:del z[k]
 return z
def fmul_fixed(a,b,p):
 z={}
 for i,u in a.items():
  for j,v in b.items():z[i+j]=(z.get(i+j,0)+u*v)%p
 return {k:v for k,v in z.items() if v}
def fpow_fixed(base,n,p):
 z={0:1}
 for _ in range(n):z=fmul_fixed(z,base,p)
 return z
def qmod(s,p):
 from fractions import Fraction
 x=Fraction(s);return (x.numerator%p)*pow(x.denominator%p,-1,p)%p
def monomial(pe,qe,c,p,I):
 inv2=pow(2,-1,p);inv2i=inv2*pow(I,-1,p)%p
 sin={1:inv2i,-1:(-inv2i)%p};cos={1:inv2,-1:inv2}
 z={0:1}
 for _ in range(pe):z=fmul_fixed(z,sin,p)
 for _ in range(qe):z=fmul_fixed(z,cos,p)
 cc=qmod(c,p);return {k:v*cc%p for k,v in z.items()}
def components(spec,p):
 roots=sp.sqrt_mod(-1,p,all_roots=True)
 if not roots:raise ValueError('prime must be 1 mod 4')
 I=int(roots[0]);out=[]
 for ds,mons in sorted(spec.items(),key=lambda z:int(z[0])):
  g={}
  for pe,qe,c in mons:g=fadd(g,monomial(int(pe),int(qe),c,p,I),p)
  out.append((int(ds),g))
 return out
def ctprod(a,b,p):
 if len(a)>len(b):a,b=b,a
 return sum(u*b.get(-k,0) for k,u in a.items())%p
def series(spec,N,p):
 comps=components(spec,p);g3,g4=comps[0][1],comps[1][1]
 p3=[{0:1}];p4=[{0:1}]
 for _ in range(2*(N-1)+1):p3.append(fmul_fixed(p3[-1],g3,p))
 for _ in range(N):p4.append(fmul_fixed(p4[-1],g4,p))
 facts=[1]*(3*N+2)
 for i in range(1,len(facts)):facts[i]=facts[i-1]*i%p
 out=[]
 for n in range(N):
  z=0
  for c in range(n+1):
   aa=2*c;bb=n-c;m=n+c
   rising=1
   for k in range(n+1,n+1+m):rising=rising*k%p
   coef=rising*pow(facts[aa],-1,p)%p*pow(facts[bb],-1,p)%p
   if m&1:coef=(-coef)%p
   z=(z+coef*ctprod(p3[aa],p4[bb],p))%p
  out.append(z)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--terms',type=int,default=200);ap.add_argument('--prime',type=int,required=True);ap.add_argument('--output',required=True);ns=ap.parse_args();rec=json.load(open(ns.model));t=time.time();seq=series(rec['monomials'],ns.terms,ns.prime);out={'example_id':rec['example_id'],'prime':ns.prime,'terms':seq,'seconds':time.time()-t};json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n');print(out['seconds'])
if __name__=='__main__':main()
