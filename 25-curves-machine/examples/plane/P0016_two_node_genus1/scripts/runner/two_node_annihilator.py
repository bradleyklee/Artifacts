#!/usr/bin/env python3
"""Order-2 Picard--Fuchs operator for the general split two-node quartic.

Family (no Weierstrass conversion):

 H = k*p^2*q^2 + beta*p^2*q + gamma*p*q^2
     + a*p^2 + b*p*q + c*q^2 + d*p + e*q + h.

On H=alpha, regard the equation as quadratic in q:

 A(p) q^2 + B(p) q + C(p)=0,
 A=k p^2+gamma p+c,
 B=beta p^2+b p+e,
 C=a p^2+d p+h-alpha.

Set y=H_q=2Aq+B. Then y^2=D_alpha(p)=B^2-4AC and

 dq/H_p = -dp/H_q = -dp/y.

The binary-quartic invariants of D_alpha produce the compact universal
order-2 annihilator printed by this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sympy as sp

alpha,p,q=sp.symbols('alpha p q')
k,beta,gamma,a,b,c,d,e,h=sp.symbols('k beta gamma a b c d e h')

H=sp.expand(k*p**2*q**2+beta*p**2*q+gamma*p*q**2+a*p**2+b*p*q+c*q**2+d*p+e*q+h)
A=sp.expand(k*p**2+gamma*p+c)
B=sp.expand(beta*p**2+b*p+e)
C=sp.expand(a*p**2+d*p+h-alpha)
D=sp.expand(B**2-4*A*C)
polyD=sp.Poly(D,p)
A4=polyD.coeff_monomial(p**4)
B3=polyD.coeff_monomial(p**3)
C2=polyD.coeff_monomial(p**2)
D1=polyD.coeff_monomial(p)
E0=polyD.coeff_monomial(1)



def operator_from_coefficients(A4v,B3v,C2v,D1v,E0v):
    Iv=sp.expand(12*A4v*E0v-3*B3v*D1v+C2v**2)
    Jv=sp.expand(72*A4v*C2v*E0v+9*B3v*C2v*D1v-27*A4v*D1v**2-27*B3v**2*E0v-2*C2v**3)
    c4v=sp.expand(4*Iv)
    c6v=sp.expand(4*Jv)
    Deltav=sp.expand(c4v**3-c6v**2)
    Gv=sp.expand(2*c4v*sp.diff(c6v,alpha)-3*c6v*sp.diff(c4v,alpha))
    p2=sp.expand(144*Deltav*Gv)
    p1=sp.expand(144*(sp.diff(Deltav,alpha)*Gv-Deltav*sp.diff(Gv,alpha)))
    p0=sp.expand(12*(sp.diff(Deltav,alpha,2)*Gv-sp.diff(Deltav,alpha)*sp.diff(Gv,alpha))
                 -9*Gv*c4v*sp.diff(c4v,alpha)**2+4*Gv*sp.diff(c6v,alpha)**2)
    return [p0,p1,p2], {'I':Iv,'Jb':Jv,'c4':c4v,'c6':c6v,'Delta':Deltav,'G':Gv}


def specialize_operator(subs):
    coeffs=[sp.expand(z.subs(subs)) for z in (A4,B3,C2,D1,E0)]
    raw,_aux=operator_from_coefficients(*coeffs)
    g=sp.gcd(sp.Poly(raw[0],alpha),sp.gcd(sp.Poly(raw[1],alpha),sp.Poly(raw[2],alpha))).as_expr()
    red=[sp.cancel(z/g) for z in raw]
    # remove rational content and normalize sign only for readable output
    dens=[sp.denom(sp.together(co)) for z in red for co in sp.Poly(z,alpha).all_coeffs()]
    den_lcm=sp.ilcm(*[int(x) for x in dens]) if dens else 1
    ints=[sp.expand(z*den_lcm) for z in red]
    contents=[sp.Poly(z,alpha).content() for z in ints if z!=0]
    try:
        cont=abs(sp.igcd(*[int(x) for x in contents])) if contents else 1
        ints=[sp.expand(z/cont) for z in ints]
        if sp.Poly(ints[-1],alpha).LC()<0:
            ints=[-z for z in ints]
        return ints,sp.factor(g)
    except TypeError:
        # Symbolic parameter content: keep the reduced rational normalization.
        return red,sp.factor(g)


def exact_differential_check(subs):
    DD=sp.expand(D.subs(subs))
    op,_=specialize_operator(subs)
    p0,p1,p2=op
    Da=sp.diff(DD,alpha)
    # p0*w+p1*w'+p2*w'' = N dp / D^(5/2)
    N=sp.expand(p0*DD**2-sp.Rational(1,2)*p1*Da*DD+sp.Rational(3,4)*p2*Da**2)
    rr=sp.symbols('r0:7')
    R=sum(rr[i]*p**i for i in range(7))
    residual=sp.Poly(sp.expand(sp.diff(R,p)*DD-sp.Rational(3,2)*R*sp.diff(DD,p)-N),p)
    sol=sp.linsolve(residual.all_coeffs(),rr)
    if sol is sp.EmptySet:
        return {'pass':False,'reason':'no degree-6 primitive'}
    tup=next(iter(sol))
    Rsol=sp.expand(R.subs(dict(zip(rr,tup))))
    check=sp.expand(sp.diff(Rsol,p)*DD-sp.Rational(3,2)*Rsol*sp.diff(DD,p)-N)
    return {
        'pass': check==0,
        'operator_degrees':[int(sp.degree(z,alpha)) for z in op],
        'primitive_p_degree':int(sp.degree(Rsol,p)),
        'primitive_alpha_degree':int(sp.degree(Rsol,alpha)),
        'operator':[str(sp.factor(z)) for z in op],
    }


def data():
    return {
      'family':str(H),
      'quadratic_in_q':{'A':str(A),'B':str(B),'C':str(C)},
      'binary_quartic_coefficients':{
          'A4':str(A4),'B3':str(B3),'C2':str(C2),'D1':str(D1),'E0':str(E0)},
      'invariants':{
          'I':'12*A4*E0 - 3*B3*D1 + C2^2',
          'Jb':'72*A4*C2*E0 + 9*B3*C2*D1 - 27*A4*D1^2 - 27*B3^2*E0 - 2*C2^3',
          'c4':'4*I','c6':'4*Jb','Delta':'c4^3-c6^2',
          'G':'2*c4*c6_prime-3*c6*c4_prime'},
      'operator':{
          'P2':'144*Delta*G',
          'P1':'144*(Delta_prime*G-Delta*G_prime)',
          'P0':'12*(Delta_double_prime*G-Delta_prime*G_prime)-9*G*c4*c4_prime^2+4*G*c6_prime^2'},
      'generic_degrees':{'I':2,'Jb':3,'Delta':5,'G':3,'P0_P1_P2_reduced':[6,7,8]},
    }


def verify():
    samples={
      'generic_1':{k:2,beta:3,gamma:5,a:7,b:11,c:13,d:17,e:19,h:0},
      'generic_2':{k:3,beta:-2,gamma:4,a:5,b:-7,c:11,d:13,e:-17,h:1},
      'generic_3':{k:-5,beta:7,gamma:2,a:3,b:8,c:-4,d:9,e:6,h:-2},
    }
    checks={name:exact_differential_check(s) for name,s in samples.items()}
    dd=sp.symbols('dd')
    edop,_=specialize_operator({k:-dd,beta:0,gamma:0,a:1,b:0,c:1,d:0,e:0,h:0})
    expected=[dd,4*(2*alpha*dd-1),4*alpha*(alpha*dd-1)]
    # compare projectively, since an annihilator is defined up to nonzero scale
    ed_ok=all(sp.expand(edop[i]*expected[2]-expected[i]*edop[2])==0 for i in range(2))
    return {
      'status':'PASS' if all(v['pass'] for v in checks.values()) and ed_ok else 'FAIL',
      'generic_exact_differential_checks':checks,
      'edwards_symbolic_check':{
        'pass':ed_ok,
        'operator':[str(z) for z in edop],
      },
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--verify',action='store_true')
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    obj=verify() if args.verify else data()
    print(json.dumps(obj,indent=2))
    if args.verify and obj['status']!='PASS':
        raise SystemExit(1)

if __name__=='__main__':
    main()
