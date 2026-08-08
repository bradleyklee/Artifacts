#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from math import gcd,lcm
from pathlib import Path
import sympy as sp

R=6;D=31

def falling(n,j):
 z=1
 for k in range(j):z*=n-k
 return z

def verify(seq,vec):
 checked=0
 for n in range(len(seq)-R):
  z=Fraction(0);t=0
  for j in range(R+1):
   for e in range(D+1):
    c=vec[t];t+=1;k=n-e+j
    if c and n>=e and k>=j and 0<=k<len(seq):z+=c*falling(k,j)*seq[k]
  if z:return False,n,str(z),checked
  checked+=1
 return True,None,None,checked

def main():
 ap=argparse.ArgumentParser();ap.add_argument('operator',type=Path);ap.add_argument('series',type=Path);ap.add_argument('--output',type=Path);ns=ap.parse_args()
 op=json.loads(ns.operator.read_text());seqrec=json.loads(ns.series.read_text());vec=[Fraction(x) for x in op['coefficients_flat']];seq=[Fraction(x) for x in seqrec['terms']]
 ok=verify(seq,vec)
 den=1
 for x in vec:den=lcm(den,x.denominator)
 ints=[x.numerator*(den//x.denominator) for x in vec]
 g=0
 for x in ints:g=gcd(g,abs(x))
 ints=[x//g for x in ints];den//=g
 if ints[-1]<0:ints=[-x for x in ints];den=-den
 alpha=sp.symbols('alpha')
 polys=[];degrees=[];supports=[]
 for j in range(R+1):
  block=ints[j*(D+1):(j+1)*(D+1)]
  poly=sum(sp.Integer(c)*alpha**e for e,c in enumerate(block))
  polys.append(poly);degrees.append(int(sp.degree(poly,alpha)));supports.append(sum(c!=0 for c in block))
 p6fac=sp.factor_list(polys[-1])
 out={
  'status':'EXACT_RATIONAL_SERIES_VERIFY_PASS' if ok[0] else 'FAIL',
  'equations_checked':ok[3],'failure_index':ok[1],'failure_residual':ok[2],
  'series_terms':len(seq),'order':R,'degree_bound':D,
  'primitive_integer_scale_denominator':str(den),
  'primitive_integer_scale_digits':len(str(abs(den))),
  'primitive_integer_coefficients':[str(x) for x in ints],
  'integer_coefficient_sha256':hashlib.sha256(('\n'.join(map(str,ints))+'\n').encode()).hexdigest(),
  'operator_degrees':degrees,'nonzero_counts':supports,
  'total_nonzero_coefficients':sum(supports),
  'maximum_integer_coefficient_digits':max(len(str(abs(x))) for x in ints),
  'P6_factorization':{'content':str(p6fac[0]),'factors':[[str(f),m] for f,m in p6fac[1]]},
 }
 if ns.output:ns.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ('primitive_integer_coefficients','P6_factorization')},indent=2))
 print('P6_FACTORIZATION',json.dumps(out['P6_factorization']))
 if not ok[0]:raise SystemExit(1)
if __name__=='__main__':main()
