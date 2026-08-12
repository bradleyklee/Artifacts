#!/usr/bin/env python3
"""Derive the two implicit surfaces from the cyclic trefoil parametrization.

The derivation uses only Laurent substitution q=exp(i phi), coefficient
matching, and linear algebra.  No Groebner basis is used.
"""
import json
from pathlib import Path
import sympy as sp

OUT = Path(__file__).resolve().parents[1] / "audit" / "implicit_derivation.json"

k,q=sp.symbols('k q')
x,y,z=sp.symbols('x y z')
I=sp.I
sin1=(q-q**-1)/(2*I); cos1=(q+q**-1)/2
sin2=(q**2-q**-2)/(2*I); cos2=(q**2+q**-2)/2
sin3=(q**3-q**-3)/(2*I)
X=sp.expand(k*sin1+sin2)
Y=sp.expand(k*cos1-cos2)
Z=sp.expand(sin3)
subs={x:X,y:Y,z:Z}


def solve_sparse_surface(basis, coeffs, scale_symbol, scale_value):
    ans=sum(a*b for a,b in zip(coeffs,basis))
    num=sp.together(ans.subs(subs)).as_numer_denom()[0]
    equations=sp.Poly(sp.expand(num),q,k).coeffs()
    sol=list(sp.linsolve(equations,coeffs))[0]
    sol=tuple(sp.simplify(v.subs(scale_symbol,scale_value)) for v in sol)
    H=sp.expand(sum(v*b for v,b in zip(sol,basis)))
    assert sp.cancel(H.subs(subs))==0
    return H,sol,len(equations)

# Cubic surface ansatz.
a=sp.symbols('a0:7')
basis1=[k*x**3,k*x*y**2,x**2*z,y**2*z,z,k**2*z,k**4*z]
H1,sol1,neq1=solve_sparse_surface(basis1,a,a[-1],-1)

# Quartic surface ansatz.
b=sp.symbols('b0:11')
basis2=[x**4,x**2*y**2,y**4,x**2*y,y**3,x**2,y**2,
        k**2*x**2,k**2*y**2,z**2,k**2*z**2]
H2,sol2,neq2=solve_sparse_surface(basis2,b,b[-1],4)

H1_expected=sp.expand(-k*x**3+3*k*x*y**2+(x**2+y**2-(1-k**2)**2)*z)
H2_expected=sp.expand((x**2+y**2)**2+(1-k**2)*(x**2+y**2)
                      -6*x**2*y+2*y**3-4*(1-k**2)*z**2)
assert sp.expand(H1-H1_expected)==0
assert sp.expand(H2-H2_expected)==0

payload={
  'parametrization':{
    'x':'k sin(phi)+sin(2 phi)',
    'y':'k cos(phi)-cos(2 phi)',
    'z':'sin(3 phi)'},
  'method':'Laurent substitution plus linear coefficient matching; no Groebner basis',
  'H1':str(sp.factor(H1)),
  'H2':str(sp.factor(H2)),
  'H1_coefficients':[str(v) for v in sol1],
  'H2_coefficients':[str(v) for v in sol2],
  'equation_counts':[neq1,neq2],
  'status':'PASS'
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload,indent=2)+'\n')
print('PASS implicit surface derivation')
print('H1 =',sp.factor(H1))
print('H2 =',sp.factor(H2))
