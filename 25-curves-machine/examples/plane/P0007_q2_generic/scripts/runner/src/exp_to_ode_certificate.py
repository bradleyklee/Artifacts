#!/usr/bin/env python3
"""Dependency-free ExpToODE: exact Laurent ODE and certificate search.

For I(alpha)=contour 1/(1-alpha*Phi(z)) dphi, z=exp(i phi),
returns L and Xi=i*V/rho^r with an exact cleared identity.
"""
from fractions import Fraction as Q
from math import factorial

def add(a,b,s=Q(1)):
    z=dict(a)
    for k,v in b.items():z[k]=z.get(k,Q(0))+s*v
    return {k:v for k,v in z.items() if v}
def scale(a,q):return {k:q*v for k,v in a.items() if q*v}
def mul(a,b):
    z={}
    for (i,j),u in a.items():
      for (k,l),v in b.items():z=add(z,{(i+k,j+l):u*v})
    return z
def power(a,n):
    z={(0,0):Q(1)}
    for _ in range(n):z=mul(z,a)
    return z
def dz0(a):return {(i,j):j*v for (i,j),v in a.items() if j} # z*d/dz
def shift_alpha(a,e):return {(i+e,j):v for (i,j),v in a.items()}

def nullspace(cols):
    rows=sorted(set().union(*(c.keys() for c in cols))); n=len(cols)
    A=[[c.get(k,Q(0)) for c in cols] for k in rows];i=0;piv=[]
    for j in range(n):
      k=next((k for k in range(i,len(A)) if A[k][j]),None)
      if k is None:continue
      A[i],A[k]=A[k],A[i];q=A[i][j];A[i]=[x/q for x in A[i]]
      for k in range(len(A)):
        if k!=i and A[k][j]:q=A[k][j];A[k]=[x-q*y for x,y in zip(A[k],A[i])]
      piv.append(j);i+=1
      if i==len(A):break
    free=[j for j in range(n) if j not in piv];out=[]
    for f in free:
      v=[Q(0)]*n;v[f]=Q(1)
      for k in range(len(piv)-1,-1,-1):
        j=piv[k];v[j]=-sum(A[k][h]*v[h] for h in free)
      out.append(v)
    return out,len(rows),len(piv)

def cos_phi(coeffs):
    # coeffs[k]*cos(k phi), returned as Laurent Phi(z).
    z={}
    for k,v in enumerate(coeffs):
      if not v:continue
      if k==0:z[(0,0)]=z.get((0,0),Q(0))+Q(v)
      else:
        z[(0,k)]=z.get((0,k),Q(0))+Q(v,2)
        z[(0,-k)]=z.get((0,-k),Q(0))+Q(v,2)
    return z

def search(phi,max_order=4,max_degree=5,verbose=True):
    one={(0,0):Q(1)};rho=add(one,shift_alpha(phi,1),Q(-1));rhoz=dz0(rho)
    maxmode=max(abs(j) for i,j in phi)
    for order in range(1,max_order+1):
      for deg in range(max_degree+1):
        ode=[];olab=[]
        for j in range(order+1):
          base=scale(mul(power(phi,j),power(rho,order-j)),Q(factorial(j)))
          for e in range(deg+1):ode.append(shift_alpha(base,e));olab.append((j,e))
        K=maxmode*order; adeg=deg+order
        cert=[];vlab=[]
        # dphi(i V/rho^order)=[-zV_z rho+order*zV*rho_z]/rho^(order+1).
        # Columns below are minus this derivative in L(f)-dphi(Xi).
        for e in range(adeg+1):
          for k in range(-K,K+1):
            if k==0:continue
            V={(e,k):Q(1)}
            col=add(mul(dz0(V),rho),scale(mul(V,rhoz),Q(-order)))
            cert.append(col);vlab.append((e,k))
        basis,rows,rank=nullspace(ode+cert)
        good=[v for v in basis if any(v[:len(ode)])]
        if verbose:print('TRY',order,deg,'cols',len(ode)+len(cert),'rows',rows,'rank',rank,'PASS',bool(good),flush=True)
        if not good:continue
        v=good[0];pivot=max(i for i,x in enumerate(v[:len(ode)]) if x);v=[x/v[pivot] for x in v]
        ps=[{} for _ in range(order+1)]
        for x,(j,e) in zip(v,olab):
          if x:ps[j][e]=x
        V={}
        for x,(e,k) in zip(v[len(ode):],vlab):
          if x:V[e,k]=x
        chk={}
        for x,col in zip(v,ode+cert):chk=add(chk,col,x)
        assert not chk
        return {'order':order,'degree':deg,'operator':ps,'V':V,'rho':rho,'verified':True}
    return None
def pstr(p):return ' + '.join(f'({v})*alpha^{e}' for e,v in sorted(p.items())).replace('+ (-','- (') or '0'
def vstr(v):return ' + '.join(f'({q})*alpha^{a}*z^{k}' for (a,k),q in sorted(v.items())).replace('+ (-','- (') or '0'
if __name__=='__main__':
    # Table 3.1 first row: Phi=4 sin(phi)^2=2-z^2-z^-2.
    phi={(0,0):Q(2),(0,2):Q(-1),(0,-2):Q(-1)}
    ans=search(phi,3,4)
    print('operator')
    for j,p in enumerate(ans['operator']):print(' p'+str(j)+' =',pstr(p))
    print('Xi = i*(',vstr(ans['V']),')/rho^'+str(ans['order']))
    print('verified',ans['verified'])
