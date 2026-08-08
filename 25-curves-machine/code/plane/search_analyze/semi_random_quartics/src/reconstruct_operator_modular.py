#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction as Q
from math import isqrt,gcd
import json,sys,time
import numpy as np
import sympy as sp
from modular_ode_screen_numpy import matrix

R=9;D=22

def null_vector_mod(A,p):
 A=A.copy();m,n=A.shape;rank=0;piv=[]
 for c in range(n):
  nz=np.flatnonzero(A[rank:,c])
  if nz.size==0:continue
  i=rank+int(nz[0])
  if i!=rank:A[[rank,i]]=A[[i,rank]]
  inv=pow(int(A[rank,c]),-1,p)
  A[rank,c:]=(A[rank,c:]*inv)%p
  rows=np.flatnonzero(A[:,c]);rows=rows[rows!=rank]
  if rows.size:
   factors=A[rows,c].copy()
   for s in range(0,len(rows),64):
    rr=rows[s:s+64];ff=factors[s:s+64]
    A[rr,c:]=(A[rr,c:]-ff[:,None]*A[rank,c:][None,:])%p
  piv.append(c);rank+=1
  if rank==m:break
 free=[c for c in range(n) if c not in piv]
 if len(free)!=1:raise ValueError((rank,n,free))
 f=free[0];x=[0]*n;x[f]=1
 for i,c in enumerate(piv):x[c]=(-int(A[i,f]))%p
 return x,f

def crt_pair(a,m,b,p):
 t=((b-a)%p)*pow(m%p,-1,p)%p
 return a+m*t

def ratrec(a,m):
 a%=m
 if a==0:return Q(0)
 B=isqrt(m//2)
 r0,r1=m,a;s0,s1=0,1
 while abs(r1)>B:
  q=r0//r1
  r0,r1=r1,r0-q*r1
  s0,s1=s1,s0-q*s1
 if s1==0:return None
 num,den=r1,s1
 if den<0:num,den=-num,-den
 g=gcd(abs(num),den);num//=g;den//=g
 if abs(num)>B or den>B or (a*den-num)%m:return None
 return Q(num,den)

def falling(n,j):
 z=1
 for k in range(j):z*=n-k
 return z

def verify(seq,vec,start=0):
 N=len(seq)
 for n in range(start,N-R):
  z=Q(0);t=0
  for j in range(R+1):
   for e in range(D+1):
    c=vec[t];t+=1
    k=n-e+j
    if c and n>=e and k>=j and 0<=k<N:z+=c*falling(k,j)*seq[k]
  if z:return False,n,z
 return True,None,None

def main():
 data=json.load(open(sys.argv[1]));seq=[Q(x) for x in data['terms']]
 ntrain=int(sys.argv[2]) if len(sys.argv)>2 else 260
 primes=[];x=65521
 while len(primes)<80:
  x=int(sp.prevprime(x));primes.append(x)
 residues=None;M=1;free0=None
 log=[]
 for idx,p in enumerate(primes,1):
  A=matrix([str(s) for s in seq],R,D,p,ntrain)
  v,f=null_vector_mod(A,p)
  if free0 is None:free0=f
  if f!=free0:raise ValueError(('free changed',free0,f,p))
  if residues is None:residues=v;M=p
  else:
   residues=[crt_pair(a,M,b,p) for a,b in zip(residues,v)];M*=p
  rec=[ratrec(a,M) for a in residues]
  solved=all(z is not None for z in rec)
  row={'prime_count':idx,'prime':p,'modulus_digits':len(str(M)),'free_column':f,'all_reconstructed':solved}
  print(row,flush=True);log.append(row)
  if solved:
   ok=verify(seq,rec,ntrain-R)
   print('VERIFY_HOLDOUT',ok,flush=True)
   if ok[0]:
    out={'example_id':'weird_quintic_p_even','order':R,'degree_bound':D,'normalization':{'free_column':f,'value':'1'},'coefficients_flat':[str(z) for z in rec],'coefficient_layout':'j-major then alpha exponent e=0..22','primes':primes[:idx],'modulus':str(M),'training_terms':ntrain,'verified_terms':len(seq),'log':log}
    json.dump(out,open('../operator_order9_degree22.json','w'),indent=2);open('../operator_order9_degree22.json','a').write('\n')
    return
 print('NOT_RECONSTRUCTED')
if __name__=='__main__':main()
