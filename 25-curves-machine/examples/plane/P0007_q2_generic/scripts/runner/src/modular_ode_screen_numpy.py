#!/usr/bin/env python3
from fractions import Fraction
import json,sys,time
import numpy as np

def falling(n,j,p):
 z=1
 for k in range(j):z=z*(n-k)%p
 return z

def qmod(x,p):
 x=Fraction(x);return (x.numerator%p)*pow(x.denominator%p,-1,p)%p

def matrix(seq,r,d,p,nterms):
 eq=nterms-r;u=(r+1)*(d+1)
 M=np.zeros((eq,u),dtype=np.int64)
 qseq=np.array([qmod(x,p) for x in seq[:nterms]],dtype=np.int64)
 col=0
 for j in range(r+1):
  for e in range(d+1):
   for n in range(e,eq):
    k=n-e+j
    if k>=j and k<nterms:
     M[n,col]=(falling(k,j,p)*int(qseq[k]))%p
   col+=1
 return M

def rank_mod(M,p):
 A=M.copy();m,n=A.shape;rank=0
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
   # chunk to keep memory modest
   for s in range(0,len(rows),64):
    rr=rows[s:s+64];ff=factors[s:s+64]
    A[rr,c:]=(A[rr,c:]-ff[:,None]*A[rank,c:][None,:])%p
  rank+=1
  if rank==m:return rank
 return rank

def scan(seq,p,nterms,pairs):
 out=[]
 for r,d in pairs:
  u=(r+1)*(d+1);eq=nterms-r
  if u>eq:
   print('SKIP',r,d,u,eq);continue
  t=time.time();M=matrix(seq,r,d,p,nterms);rk=rank_mod(M,p);dt=time.time()-t
  print('PAIR',r,d,'shape',M.shape,'rank',rk,'nullity',u-rk,'sec',round(dt,3),flush=True)
  if rk<u:out.append((r,d,u-rk))
 return out

if __name__=='__main__':
 data=json.load(open(sys.argv[1]));seq=data['terms'];p=int(sys.argv[2]);n=int(sys.argv[3])
 pairs=[]
 if len(sys.argv)>4:
  for x in sys.argv[4:]:
   r,d=x.split(',');pairs.append((int(r),int(d)))
 else:
  for r in range(6,17):
   for d in range(5,18):
    if (r+1)*(d+1)<=n-r:pairs.append((r,d))
 print('HITS',scan(seq,p,n,pairs))
