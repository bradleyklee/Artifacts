#!/usr/bin/env python3
from fractions import Fraction as F
import argparse,json,time,math
import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

def falling(n,j):
 z=1
 for k in range(j):z*=n-k
 return z

def main():
 ap=argparse.ArgumentParser();ap.add_argument('series');ap.add_argument('--order',type=int,required=True);ap.add_argument('--degree',type=int,required=True);ap.add_argument('--terms',type=int,required=True);ap.add_argument('--output',required=True)
 ns=ap.parse_args();seq=[F(x) for x in json.load(open(ns.series))['terms']];R=ns.order;D=ns.degree;N=ns.terms
 eq=N-R;u=(R+1)*(D+1)
 rows=[]
 for n in range(eq):
  row=[]
  for j in range(R+1):
   for e in range(D+1):
    k=n-e+j
    v=F(0)
    if n>=e and k>=j and 0<=k<len(seq):v=F(falling(k,j))*seq[k]
    row.append(QQ(v.numerator,v.denominator))
  rows.append(row)
 print('shape',eq,u,flush=True);t=time.time();M=DomainMatrix.from_list(rows,QQ);B=M.nullspace();print('nullspace',B.shape,'sec',time.time()-t,flush=True)
 BM=B.to_Matrix();assert BM.rows==1
 v=[sp.Rational(x) for x in BM.row(0)]
 # primitive integer normalization
 den=sp.ilcm(*[sp.denom(x) for x in v]);w=[sp.Integer(x*den) for x in v];g=abs(math.gcd(*[int(x) for x in w if x]));w=[x//g for x in w]
 # sign based last nonzero
 if next(x for x in reversed(w) if x)<0:w=[-x for x in w]
 out={'order':R,'degree_bound':D,'terms_used':N,'matrix_shape':[eq,u],'nullity':BM.rows,'coefficients_flat':[str(x) for x in w]}
 json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
 print('digits_max',max(len(str(abs(int(x)))) for x in w),'nonzero',sum(bool(x) for x in w),flush=True)
if __name__=='__main__':main()
