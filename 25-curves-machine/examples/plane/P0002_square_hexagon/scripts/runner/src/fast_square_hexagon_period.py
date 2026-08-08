from fractions import Fraction as Q
from math import comb

def mul(a,b):
 z={}
 for i,u in a.items():
  for j,v in b.items():z[i+j]=z.get(i+j,0)+u*v
 return {k:v for k,v in z.items() if v}

def coeffs(N):
 # c_r for r=0..N-1, where period=sum c_r alpha^r
 A={-4:1,0:-2,4:1} # 2A
 B={-6:1,0:2,6:1}  # 2B
 Ap=[{0:1}];Bp=[{0:1}]
 for _ in range(N):Ap.append(mul(Ap[-1],A));Bp.append(mul(Bp[-1],B))
 out=[]
 for r in range(N):
  n=r+1;s=Q(0)
  for l in range((n-1)//2+1):
   k=n-1-2*l;m=k+l
   ct=sum(v*Bp[l].get(-mode,0) for mode,v in Ap[k].items())
   # 2^(1-n) (-1)^m C(n+m-1,m) C(m,k) * CT(A2^k B2^l)/2^(2m)
   s += Q(((-1)**m)*comb(n+m-1,m)*comb(m,k)*ct, 2**(n-1+2*m))
  out.append(s)
 return out
if __name__=='__main__':
 import sys,time
 N=int(sys.argv[1]) if len(sys.argv)>1 else 110
 t=time.time();q=coeffs(N);print('seconds',time.time()-t)
 for n,x in enumerate(q[-5:],N-5):print(n,x)
 open('/tmp/fast_period_terms.txt','w').write('\n'.join(map(str,q))+'\n')
