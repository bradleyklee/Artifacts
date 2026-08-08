#!/usr/bin/env python3
"""Exact polynomial-Hamiltonian period ODE and certificate pipeline.

Scope of this reference implementation:
  K(p,q)=p^2+q^2+sum c_i Re(q+i p)^d_i,
with rational c_i, a Morse center at the origin, and a constant nonzero leading
coefficient in p.  It generates exact period coefficients, guesses an ODE,
and proves it by solving for an exact differential certificate.
"""
from fractions import Fraction as F
from math import comb,factorial,prod
from itertools import product
from exp_to_ode_certificate import nullspace
from exact_period_series import angular,fmul
from guess_ode import guess

# Polynomials in (alpha,p,q), keyed by exponent triples.
def add(a,b,c=F(1)):
    z=dict(a)
    for m,v in b.items():z[m]=z.get(m,F(0))+c*v
    return {m:v for m,v in z.items() if v}
def scale(a,c):return {m:c*v for m,v in a.items() if c*v}
def mul(a,b):
    z={}
    for (i,j,k),u in a.items():
      for (l,m,n),v in b.items():z=add(z,{(i+l,j+m,k+n):u*v})
    return z
def power(a,n):
    z={(0,0,0):F(1)}
    for _ in range(n):z=mul(z,a)
    return z
def der(a,var):
    z={}
    for e,v in a.items():
      if e[var]:
        w=list(e);c=w[var];w[var]-=1;z[tuple(w)]=c*v
    return z
def mono(a,p,q):return {(a,p,q):F(1)}

def real_mode(degree,coefficient=F(1)):
    """coefficient*Re(q+i*p)^degree as an (alpha,p,q) polynomial."""
    z={}
    for j in range(0,degree+1,2):
        z[0,j,degree-j]=coefficient*F(comb(degree,j))*(-1)**(j//2)
    return z

def make_hamiltonian(terms):
    K={(0,2,0):F(1),(0,0,2):F(1)}
    for t in terms:K=add(K,real_mode(t['degree'],F(t['coefficient'])))
    return K

def curve_reducer(K):
    d=max(p for a,p,q in K)
    leads={(a,q):c for (a,p,q),c in K.items() if p==d}
    if set(leads)!={(0,0)}:raise ValueError('leading p coefficient must be a nonzero rational constant')
    lead=leads[0,0]
    lower={m:c for m,c in K.items() if m[1]<d}
    # p^d=(alpha-lower)/lead.
    repl=add({(1,0,0):F(1,1)/lead},scale(lower,-F(1,1)/lead))
    def reduce(f):
        z=dict(f)
        while True:
            bad=next((m for m in z if m[1]>=d),None)
            if bad is None:return {m:v for m,v in z.items() if v}
            c=z.pop(bad);a,p,q=bad
            z=add(z,scale(mul(mono(a,p-d,q),repl),c))
    return d,reduce

def compositions_weighted(target,weights):
    out=[]
    def rec(i,left,row):
        if i==len(weights):
            if left==0:out.append(tuple(row))
            return
        w=weights[i]
        for k in range(left//w+1):rec(i+1,left-k*w,row+[k])
    rec(0,target,[]);return out

def period_coefficients(terms,N):
    """Lagrange-inversion coefficients of T(alpha)/(2*pi)."""
    weights=[t['degree']-2 for t in terms]
    if any(w<=0 for w in weights):raise ValueError('perturbation degrees must exceed 2')
    maxks=[2*(N-1)//w for w in weights]
    fpows=[]
    for t,mx in zip(terms,maxks):
        a=[{0:F(1)}]
        for _ in range(mx):a.append(fmul(a[-1],angular(t.get('mode',t['degree']))))
        fpows.append(a)
    out=[]
    for n in range(N):
        z=F(0)
        for ks in compositions_weighted(2*n,weights):
            m=sum(ks)
            coeff=F((-1)**m*prod(range(n+1,n+1+m)),prod(factorial(k) for k in ks))
            four={0:F(1)}
            for arr,k,t in zip(fpows,ks,terms):
                four=fmul(four,arr[k]);coeff*=F(t['coefficient'])**k
            z+=coeff*four.get(0,F(0))
        out.append(z)
    return out

def operator_polys(ps):
    return [{(e,0,0):F(c) for e,c in p.items()} for p in ps]

def certificate_search(K,ps,max_alpha_degree=7,max_q_degree=20,verbose=True):
    """Prove sum p_j D_alpha^j integral=0 by an exact differential."""
    order=len(ps)-1;d,reduce=curve_reducer(K)
    Kp=der(K,1);Kq=der(K,2);Kpp=der(Kp,1);Kpq=der(Kp,2)
    # D_alpha^j(2/Kp)=N_j/Kp^(2j+1).
    nums=[{(0,0,0):F(2)}]
    for j in range(order):
        nums.append(add(mul(Kp,der(nums[-1],1)),mul(nums[-1],Kpp),-F(2*j+1)))
    NH={};P=operator_polys(ps)
    for j in range(order+1):NH=add(NH,mul(P[j],mul(nums[j],power(Kp,2*(order-j)))))
    NH=reduce(NH)
    m=2*order-1;J=add(mul(Kp,Kpq),mul(Kpp,Kq),F(-1))
    def image(V):
        transport=add(mul(Kp,der(V,2)),mul(Kq,der(V,1)),F(-1))
        return reduce(add(mul(Kp,transport),mul(V,J),F(-m)))
    for da in range(max_alpha_degree+1):
      for dq in range(2,max_q_degree+1,2):
        labs=[];cols=[]
        for a in range(da+1):
          for p in range(d):
            for q in range(dq+1):labs.append((a,p,q));cols.append(image(mono(a,p,q)))
        basis,rows,rank=nullspace(cols+[scale(NH,F(-1))])
        good=[v for v in basis if v[-1]]
        if verbose:print('CERT_TRY',da,dq,'unknowns',len(cols),'rows',rows,'rank',rank,'PASS',bool(good),flush=True)
        if good:
            v=[x/good[0][-1] for x in good[0]];V={m:x for m,x in zip(labs,v[:-1]) if x}
            residue=add(image(V),NH,F(-1));assert not residue
            return {'V':V,'denominator_power':m,'residual':residue,
                    'metadata':{'alpha_degree':da,'q_degree':dq,'p_basis_degree':d,
                                'unknowns':len(cols),'rows':rows,'rank':rank,'terms':len(V)}}
    return None

def run(terms,series_terms=48,max_order=4,max_degree=7,holdout=7,
        cert_alpha_degree=7,cert_q_degree=20,verbose=True):
    K=make_hamiltonian(terms)
    seq=period_coefficients(terms,series_terms)
    ans=guess(seq,max_order,max_degree,holdout)
    if ans is None:return {'hamiltonian':K,'series':seq,'operator':None,'certificate':None}
    order,degree,ps=ans
    cert=certificate_search(K,ps,cert_alpha_degree,cert_q_degree,verbose)
    return {'hamiltonian':K,'series':seq,'operator':{'order':order,'degree':degree,'coefficients':ps},'certificate':cert}

if __name__=='__main__':
    # Regression: the proved triangular+square showcase.
    result=run([{'degree':3,'mode':3,'coefficient':'1'},
                {'degree':4,'mode':4,'coefficient':'1/4'}],
               series_terms=40,max_order=2,max_degree=5,holdout=7,
               cert_alpha_degree=4,cert_q_degree=10)
    assert result['operator'] and result['certificate'] and not result['certificate']['residual']
    print('PIPELINE_EXACT_PASS',result['operator']['order'],result['operator']['degree'],
          result['certificate']['metadata'])
