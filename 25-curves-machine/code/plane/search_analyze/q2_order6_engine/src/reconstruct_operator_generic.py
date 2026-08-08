#!/usr/bin/env python3
from fractions import Fraction as Q
from math import isqrt,gcd
import argparse,json
import sympy as sp
from modular_ode_screen_numpy import matrix
from reconstruct_operator_modular import null_vector_mod,crt_pair,ratrec,falling

def verify(seq,vec,R,D,start=0):
 N=len(seq)
 for n in range(start,N-R):
  z=Q(0);t=0
  for j in range(R+1):
   for e in range(D+1):
    c=vec[t];t+=1;k=n-e+j
    if c and n>=e and k>=j and 0<=k<N:z+=c*falling(k,j)*seq[k]
  if z:return False,n,str(z)
 return True,None,None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('series');ap.add_argument('--order',type=int,required=True);ap.add_argument('--degree',type=int,required=True);ap.add_argument('--train',type=int,required=True);ap.add_argument('--output',required=True);ap.add_argument('--id',default='case');ap.add_argument('--max-primes',type=int,default=100)
 ns=ap.parse_args();data=json.load(open(ns.series));seq=[Q(x) for x in data['terms']];R=ns.order;D=ns.degree
 primes=[];x=65521
 while len(primes)<ns.max_primes:
  x=int(sp.prevprime(x));primes.append(x)
 residues=None;M=1;free0=None;log=[]
 for idx,p in enumerate(primes,1):
  A=matrix([str(s) for s in seq],R,D,p,ns.train);v,f=null_vector_mod(A,p)
  if free0 is None:free0=f
  if f!=free0:
   print('SKIP_FREE_CHANGE',p,f,free0,flush=True);continue
  if residues is None:residues=v;M=p
  else:residues=[crt_pair(a,M,b,p) for a,b in zip(residues,v)];M*=p
  rec=[ratrec(a,M) for a in residues];solved=all(z is not None for z in rec)
  row={'prime_count':idx,'prime':p,'modulus_digits':len(str(M)),'free_column':f,'all_reconstructed':solved};log.append(row);print(row,flush=True)
  if solved:
   ok=verify(seq,rec,R,D,ns.train-R);print('VERIFY_HOLDOUT',ok,flush=True)
   if ok[0]:
    out={'example_id':ns.id,'order':R,'degree_bound':D,'normalization':{'free_column':f,'value':'1'},'coefficients_flat':[str(z) for z in rec],'coefficient_layout':f'j-major then alpha exponent e=0..{D}','primes':primes[:idx],'modulus':str(M),'training_terms':ns.train,'verified_terms':len(seq),'log':log,'status':'EXACT_OPERATOR_RECONSTRUCTED'}
    json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n');return
 print('NOT_RECONSTRUCTED')
if __name__=='__main__':main()
