#!/usr/bin/env python3
import argparse,json,time
from fractions import Fraction as F
from math import factorial

def fadd(a,b):
 z=dict(a)
 for k,v in b.items():
  z[k]=z.get(k,F(0))+v
  if not z[k]:del z[k]
 return z
def fmul(a,b):
 z={}
 for i,u in a.items():
  for j,v in b.items():z[i+j]=z.get(i+j,F(0))+u*v
 return {k:v for k,v in z.items() if v}
def fpow(base,n):
 z={0:F(1)}
 for _ in range(n):z=fmul(z,base)
 return z
def monomial(pe,qe,c):
 # p=sin(phi), q=cos(phi), Laurent variable z=e^{i phi}; constant terms are rational.
 I2={1:F(-1,2),-1:F(1,2)} # coefficients with common factor 1/i suppressed carefully below
 # Use formal pairs A+iB? Easier: complex rational represented tuple (re,im).
 raise RuntimeError('unused')

def cmul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def cadd(x,y):return (x[0]+y[0],x[1]+y[1])
def cscale(x,c):return (x[0]*c,x[1]*c)
def cfadd(a,b):
 z=dict(a)
 for k,v in b.items():
  z[k]=cadd(z.get(k,(F(0),F(0))),v)
  if z[k]==(0,0):del z[k]
 return z
def cfmul(a,b):
 z={}
 for i,u in a.items():
  for j,v in b.items():z[i+j]=cadd(z.get(i+j,(F(0),F(0))),cmul(u,v))
 return {k:v for k,v in z.items() if v!=(0,0)}
def cfpow(base,n):
 z={0:(F(1),F(0))}
 for _ in range(n):z=cfmul(z,base)
 return z

def angular_monomial(pe,qe,c):
 sin={1:(F(0),F(-1,2)),-1:(F(0),F(1,2))}
 cos={1:(F(1,2),F(0)),-1:(F(1,2),F(0))}
 z={0:(F(1),F(0))}
 for _ in range(pe):z=cfmul(z,sin)
 for _ in range(qe):z=cfmul(z,cos)
 return {k:cscale(v,F(c)) for k,v in z.items()}

def components(spec):
 out={3:{},4:{}}
 for ds,mons in spec.items():
  g={}
  for pe,qe,c in mons:g=cfadd(g,angular_monomial(int(pe),int(qe),F(c)))
  out[int(ds)]=g
 return out[3],out[4]

def ctprod(a,b):
 z=(F(0),F(0))
 for k,u in a.items():z=cadd(z,cmul(u,b.get(-k,(F(0),F(0)))))
 assert z[1]==0
 return z[0]

def period_series(spec,N):
 g3,g4=components(spec)
 p3=[{0:(F(1),F(0))}];p4=[{0:(F(1),F(0))}]
 for _ in range(2*(N-1)):p3.append(cfmul(p3[-1],g3))
 for _ in range(N):p4.append(cfmul(p4[-1],g4))
 out=[]
 for n in range(N):
  z=F(0)
  for c in range(n+1):
   aa=2*c;bb=n-c;m=n+c
   rising=1
   for k in range(n+1,n+1+m):rising*=k
   coef=F(((-1)**m)*rising,factorial(aa)*factorial(bb))
   z+=coef*ctprod(p3[aa],p4[bb])
  out.append(z)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--terms',type=int,default=24);ap.add_argument('--output',required=True);ns=ap.parse_args()
 rec=json.load(open(ns.model));t=time.time();seq=period_series(rec['monomials'],ns.terms)
 out={'example_id':rec['example_id'],'terms':[str(x) for x in seq],'seconds':time.time()-t}
 with open(ns.output,'w') as f:json.dump(out,f,indent=2);f.write('\n')
 print(rec['example_id'],out['seconds'],', '.join(map(str,seq[:8])))
if __name__=='__main__':main()
