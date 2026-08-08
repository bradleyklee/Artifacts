#!/usr/bin/env python3
from fractions import Fraction as Q
from math import factorial, prod
import argparse,json
from q1_model import components
from generic_even_p_quintic import fmul

def ctprod(a,b):
 if len(a)>len(b):a,b=b,a
 return sum((u*b.get(-k,Q(0)) for k,u in a.items()),Q(0))

def series(N):
 comps=components(); assert [d for d,g in comps]==[3,4]
 g3=comps[0][1];g4=comps[1][1]
 p3=[{0:Q(1)}];p4=[{0:Q(1)}]
 for _ in range(2*(N-1)+1):p3.append(fmul(p3[-1],g3))
 for _ in range(N):p4.append(fmul(p4[-1],g4))
 out=[]
 for n in range(N):
  z=Q(0)
  # k3+2*k4=2n; k3=2c, k4=n-c
  for c in range(n+1):
   a=2*c;b=n-c;m=a+b # n+c
   rising=prod(range(n+1,n+1+m)) if m else 1
   coeff=Q(((-1)**m)*rising,factorial(a)*factorial(b))
   z += coeff*ctprod(p3[a],p4[b])
  out.append(z)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--terms',type=int,default=160);ap.add_argument('--output')
 ns=ap.parse_args();seq=series(ns.terms)
 rec={'example_id':'semi_random_quartic_q1_p_even','E':'p**2+q**2+(2*p**4-3*p**2*q**2+5*q**4)/8+(3*p**2*q-2*q**3)/10','H':'E/2','symmetry':{'p_reflection':True,'q_reflection':False},'quantity':'T(alpha)/(2*pi)','method':'weighted Lagrange inversion specialized to cubic+quartic','terms':[str(x) for x in seq]}
 txt=json.dumps(rec,indent=2)+'\n'
 if ns.output:open(ns.output,'w').write(txt)
 else:print(txt)
if __name__=='__main__':main()
