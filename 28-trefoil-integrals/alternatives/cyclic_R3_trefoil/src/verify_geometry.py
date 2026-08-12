#!/usr/bin/env python3
"""Exact SymPy audit of the cyclic R^3 trefoil family.

Starts from the explicit trigonometric parametrization and the two independently
derived implicit surfaces.  Checks the tangent cross-product factor, evaluates
the period by residues, verifies the algebraic relation, the minimal first-order
ODE, a nonminimal second-order ODE and its factorization, a rational telescoping
certificate, and the integral power-series normalization.
"""
import json
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit'/'symbolic_results.json'

k,x,y,z,q,c=sp.symbols('k x y z q c')
I=sp.I
sin1=(q-q**-1)/(2*I); cos1=(q+q**-1)/2
sin2=(q**2-q**-2)/(2*I); cos2=(q**2+q**-2)/2
sin3=(q**3-q**-3)/(2*I)
X=sp.expand(k*sin1+sin2)
Y=sp.expand(k*cos1-cos2)
Z=sp.expand(sin3)
H1=-k*x**3+3*k*x*y**2+(x**2+y**2-(1-k**2)**2)*z
H2=(x**2+y**2)**2+(1-k**2)*(x**2+y**2)-6*x**2*y+2*y**3-4*(1-k**2)*z**2
subs={x:X,y:Y,z:Z}
assert sp.cancel(H1.subs(subs))==0
assert sp.cancel(H2.subs(subs))==0

# Tangent field.
g1=sp.Matrix([sp.diff(H1,v) for v in (x,y,z)])
g2=sp.Matrix([sp.diff(H2,v) for v in (x,y,z)])
cross=sp.Matrix([sp.factor(v.subs(subs)) for v in g1.cross(g2)])
rphi=sp.Matrix([sp.factor(I*q*sp.diff(v,q)) for v in (X,Y,Z)])
A=q**6-k*(1+k**2)*q**3+(2*k**2-1)
B=(2*k**2-1)*q**6-k*(1+k**2)*q**3+1
Lambda=sp.factor(2*A*B/q**6)
for j in range(3):
    assert sp.cancel(cross[j]-Lambda*rphi[j])==0

# Residue evaluation with Q=exp(3 i phi).
Q=sp.symbols('Q')
A3=Q**2-k*(1+k**2)*Q+(2*k**2-1)
B3=(2*k**2-1)*Q**2-k*(1+k**2)*Q+1
disc=(1-k**2)*sp.sqrt(k**2+4)
a_minus=(k*(1+k**2)-disc)/2
a_plus=(k*(1+k**2)+disc)/2
b_inside=1/a_plus
res1=sp.cancel(a_minus/(sp.diff(A3,Q).subs(Q,a_minus)*B3.subs(Q,a_minus)))
res2=sp.cancel(b_inside/(A3.subs(Q,b_inside)*sp.diff(B3,Q).subs(Q,b_inside)))
res_sum=sp.radsimp(sp.factor(res1+res2))
F=(1+k**2)/(k*(1-k**2)**3*sp.sqrt(k**2+4))
assert sp.simplify(res_sum-F)==0

# Algebraic relation for Y=T/pi.
assert sp.factor(k**2*(1-k**2)**6*(k**2+4)*F**2-(1+k**2)**2)==0

# Minimal first-order annihilator.
Q1=k*(k**2-1)*(k**2+1)*(k**2+4)
Q0=2*(k**2+2)*(3*k**4+8*k**2-1)
assert sp.factor(Q1*sp.diff(F,k)+Q0*F)==0

# A valid nonminimal second-order annihilator and its factorization.
P0=24*k*(6-12*k**2-k**4+2*k**6)
P1=-(1-k**2)*(16-102*k**2+11*k**4+15*k**6)
P2=-k*(1-k**2)**2*(2-k**2)*(4+k**2)
L2=sp.factor(P0*F+P1*sp.diff(F,k)+P2*sp.diff(F,k,2))
assert L2==0
G=1/(1-k**2)**3
assert sp.factor(P0*G+P1*sp.diff(G,k)+P2*sp.diff(G,k,2))==0
M1=(k**2-1)*(k**2-2)/(k**2+1)
M0=2*k*(k**2-3)/(k**2+1)
assert sp.simplify(M1*Q1-P2)==0
assert sp.simplify(M1*(sp.diff(Q1,k)+Q0)+M0*Q1-P1)==0
assert sp.simplify(M1*sp.diff(Q0,k)+M0*Q0-P0)==0

# Rational differential certificate for L2 applied to the period integrand.
H=(4-7*k**2+6*k**4+k**6-4*k**3*(1+k**2)*c+4*(2*k**2-1)*c**2)
f=1/(2*H)
Rc=((-32*k**4+128*k**2-56)*c**3
    +(32*k**7-80*k**5-112*k**3)*c**2
    +(-8*k**10+24*k**8-4*k**6+148*k**4-20*k**2+60)*c
    +k**11+9*k**9-75*k**7+79*k**5-62*k**3-32*k)
N=-sp.Rational(2,3)*k*Rc
dXi=sp.cancel(3*(c*N*H-(1-c**2)*(sp.diff(N,c)*H-2*N*sp.diff(H,c)))/H**3)
assert sp.factor(P0*f+P1*sp.diff(f,k)+P2*sp.diff(f,k,2)-dXi)==0

# Integral normalization x=k^2/16, A(x)=2kT/pi.
t=sp.symbols('t')
Af=(1+16*t)/((1-16*t)**3*sp.sqrt(1+4*t))
assert sp.factor((1+4*t)*(1-16*t)**6*Af**2-(1+16*t)**2)==0
series=sp.series(Af,t,0,16).removeO().expand()
coeff=[sp.Integer(series.coeff(t,n)) for n in range(16)]
assert all(a.is_Integer for a in coeff)
for n in range(13):
    am1=coeff[n-1] if n>=1 else 0
    am2=coeff[n-2] if n>=2 else 0
    assert (n+1)*coeff[n+1]==(62-4*n)*coeff[n]+256*(n+2)*am1+512*(2*n+1)*am2
for n,a in enumerate(coeff):
    conv=sum((-1)**j*sp.binomial(2*j,j)*(n-j+1)**2*16**(n-j) for j in range(n+1))
    assert sp.simplify(conv-a)==0

payload={
 'parametrization':{'x':'k sin(phi)+sin(2 phi)','y':'k cos(phi)-cos(2 phi)','z':'sin(3 phi)'},
 'H1':str(sp.factor(H1)),'H2':str(sp.factor(H2)),
 'tangent_scale':'2*A(q)*B(q)/q^6',
 'period_over_pi':str(F),
 'algebraic_relation':'k^2(1-k^2)^6(k^2+4)Y^2-(1+k^2)^2=0',
 'minimal_first_order':{'Q1':str(sp.factor(Q1)),'Q0':str(sp.factor(Q0))},
 'second_order':{'P2':str(sp.factor(P2)),'P1':str(sp.factor(P1)),'P0':str(sp.factor(P0))},
 'integral_normalization':{
   'x':'k^2/16','A(x)':'(1+16x)/((1-16x)^3 sqrt(1+4x))',
   'algebraic':'(1+4x)(1-16x)^6 A(x)^2-(1+16x)^2=0',
   'coefficients':[int(v) for v in coeff]},
 'status':'PASS'}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload,indent=2)+'\n')
print('PASS implicit surfaces and tangent field')
print('PASS residue period = pi*(1+k^2)/(k*(1-k^2)^3*sqrt(k^2+4))')
print('PASS algebraic relation and minimal order-1 ODE')
print('PASS nonminimal order-2 ODE, factorization, rational certificate')
print('PASS integral normalization and recurrence')
print('first coefficients:',coeff[:10])
