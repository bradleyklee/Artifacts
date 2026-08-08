#!/usr/bin/env python3
"""Exact and high-precision checks for the triangle-rectangle certificate."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import mpmath as mp
import sympy as sp


# Reproduce the midpoint action-quantized contour levels used by the figure.
HERE = Path(__file__).resolve().parent
level_generator = HERE / "generate_quantized_levels.py"
if not level_generator.is_file():
    level_generator = HERE / "scripts" / "generate_quantized_levels.py"
subprocess.run([sys.executable, str(level_generator), "--check"], cwd=level_generator.parent.parent if level_generator.parent.name == "scripts" else HERE, check=True, stdout=subprocess.PIPE, text=True)

# Symbols and curve.
a,p,q,x,beta,t=sp.symbols('a p q x beta t')
F=p**2+q**2+q**3-3*p**2*q+sp.Rational(1,4)*(q**2-3*p**2)**2
rho=sp.factor(sp.diff(F,p))
omega=2/rho

P0=3*a*(9*a-16)
P1=216*a**3-195*a**2-28*a+8
P2=a*(3*a-2)*(4*a-1)*(9*a+4)

# Compact exact certificate, x=q+1.
X=q+1
V=sp.expand(X*(
    a**3*(486*p**2-162*X**2+1080)
    +a**2*(1134*p**2*X**2-405*p**2-162*X**4+189*X**2+105)
    +a*(-108*p**2*X**4-648*p**2*X**2+1002*p**2+36*X**6-156*X**4+114*X**2+70)
    +(-108*p**2*X**4+468*p**2*X**2-432*p**2+36*X**6-144*X**4+188*X**2-80)
))

assert sp.factor(rho-p*(9*p**2-3*(q+1)**2+5))==0
assert sp.expand(F.subs(q,-2-q)-F)==0
mu=sp.symbols('mu')
Fmu=p**2+q**2+(q**3-3*p**2*q)+mu*(q**2-3*p**2)**2
reflection_defect=-2*(4*mu-1)*(q+1)*(3*p**2-q**2-2*q-2)
assert sp.expand(Fmu.subs(q,-2-q)-Fmu-reflection_defect)==0
assert sp.factor(P1-(sp.diff(P2,a)-6*P2/(3*a-2)))==0

# Exact differential certificate on F=a.
Dalpha=lambda f: sp.diff(f,p)/rho
Aomega=P0*omega+P1*Dalpha(omega)+P2*Dalpha(Dalpha(omega))
Xi=V/rho**3
dXi_curve=sp.diff(Xi,q)-sp.diff(F,q)/rho*sp.diff(Xi,p)
assert sp.factor(sp.together(Aomega.subs(a,F)-dXi_curve.subs(a,F)))==0

# Critical points and Abel-Wick center.
for pt,val,hdet in [
    ({p:0,q:0},sp.Integer(0),sp.Integer(4)),
    ({p:0,q:-2},sp.Integer(0),sp.Integer(4)),
    ({p:0,q:-1},sp.Rational(1,4),sp.Integer(-5)),
]:
    assert sp.simplify(sp.diff(F,p).subs(pt))==0
    assert sp.simplify(sp.diff(F,q).subs(pt))==0
    assert sp.simplify(F.subs(pt))==val
    assert sp.factor(sp.hessian(F,(p,q)).subs(pt).det())==hdet
U,Q=sp.symbols('U Q', real=True)
Fw=sp.expand(F.subs({p:sp.I*U,q:-1+Q}))
expected=sp.Rational(1,4)+(9*U**4+6*U**2*Q**2-10*U**2+Q**4-2*Q**2)/4
assert sp.expand(Fw-expected)==0
# Tangent-matched Abel-Wick display levels: p=iU preserves alpha.
assert sp.expand(F.subs(p, sp.I*U) - ( -U**2 + q**2 + q**3 + 3*U**2*q + sp.Rational(1,4)*(q**2+3*U**2)**2 )) == 0
Vaxis = sp.factor(F.subs(p,0))
Waxis = sp.factor(Fw.subs({U:0,Q:q+1}))
assert sp.expand(Vaxis-Waxis)==0
assert sp.diff(F,p).subs(p,0)==0
assert sp.diff(Fw,U).subs(U,0)==0
Hwick=Fw/2
assert sp.hessian(Hwick,(U,Q)).subs({U:0,Q:0})==sp.diag(-sp.Rational(5,2),-sp.Rational(1,2))
assert sp.sqrt(sp.hessian(Hwick,(U,Q)).subs({U:0,Q:0}).det())==sp.sqrt(5)/2

# Hypergeometric pullback proof.
chi=-27*a**2*(4*a-1)*(9*a+4)**2/(4*(1+9*a**2)**3)
g=(1+9*a**2)**(-sp.Rational(1,4))
F0,F1=sp.symbols('F0 F1')
F2=(sp.Rational(5,144)*F0-(1-sp.Rational(3,2)*chi)*F1)/(chi*(1-chi))
y1=sp.diff(g,a)*F0+g*F1*sp.diff(chi,a)
y2=sp.diff(g,a,2)*F0+2*sp.diff(g,a)*F1*sp.diff(chi,a)+g*F2*sp.diff(chi,a)**2+g*F1*sp.diff(chi,a,2)
L=sp.factor(P2*y2+P1*y1+P0*g*F0)
assert sp.factor(sp.diff(L,F0))==0 and sp.factor(sp.diff(L,F1))==0

# Integer real series A(x)=T1(4x).
def real_terms(N:int):
    out=[sp.Integer(0)]*N
    out[0]=1
    if N>1: out[1]=0
    for n in range(1,N-1):
        g0=lambda k: out[k] if k>=0 else 0
        num=(n*(13*n+1)*g0(n)+6*(17*n*n+14*n-15)*g0(n-1)-216*(2*n-3)**2*g0(n-2))
        out[n+1],rem=divmod(int(num),(n+1)**2)
        assert rem==0
        out[n+1]=sp.Integer(out[n+1])
    return out
A=real_terms(1000)
assert A[:10]==[1,0,24,120,2520,25200,397320,5045040,74594520,1037356320]

# Analytic Abel-Wick branch T2 at alpha=1/4, T2(1/4)=1.
p2b=[sp.Integer(0),-sp.Rational(125,16),-sp.Rational(95,4),sp.Integer(57),sp.Integer(108)]
p1b=[-sp.Rational(125,16),-sp.Integer(85),-sp.Integer(33),sp.Integer(216)]
p0b=[-sp.Rational(165,16),-sp.Rational(69,2),sp.Integer(27)]
def complex_coeffs(N:int):
    c=[sp.Rational(0)]*N;c[0]=1
    for n in range(N-1):
        den=p2b[1]*(n+1)*n+p1b[0]*(n+1)
        rhs=sp.Rational(0)
        for j,co in enumerate(p2b):
            k=n-j+2
            if 0<=k<=n: rhs+=co*k*(k-1)*c[k]
        for j,co in enumerate(p1b):
            k=n-j+1
            if 0<=k<=n: rhs+=co*k*c[k]
        for j,co in enumerate(p0b):
            k=n-j
            if 0<=k<=n: rhs+=co*c[k]
        c[n+1]=sp.simplify(-rhs/den)
    return c
C=complex_coeffs(500)
assert C[:6]==[1,-sp.Rational(33,25),sp.Rational(1461,500),-sp.Rational(97701,12500),sp.Rational(23249457,1000000),-sp.Rational(46169514657,625000000)]
Ci=[sp.simplify(C[n]*(-100)**n) for n in range(40)]
assert all(v.is_Integer for v in Ci)
assert Ci[:6]==[1,132,29220,7816080,2324945700,738712234512]

# Abel identity at common interior points.
mp.mp.dps=80
def mpr(v): return mp.mpf(str(sp.N(v,90)))
for st in ['0.06','0.10','0.14','0.18','0.20']:
    z=mp.mpf(st)
    T1=mp.fsum(mp.mpf(A[n])*(z/4)**n for n in range(700))
    T1p=mp.fsum(mp.mpf(A[n])*n*(z/4)**(n-1)/4 for n in range(1,700))
    b=z-mp.mpf('0.25')
    T2=mp.fsum(mpr(C[n])*b**n for n in range(450))
    T2p=mp.fsum(n*mpr(C[n])*b**(n-1) for n in range(1,450))
    factor=z*(3*z-2)*(4*z-1)*(9*z+4)/(3*z-2)**2
    assert abs(factor*(T2*T1p-T1*T2p)-mp.sqrt(5)/mp.pi)<mp.mpf('1e-48')

# Hypergeometric values agree with the real series.
for st in ['0.01','0.05','0.08','0.10']:
    z=mp.mpf(st)
    ch=-27*z**2*(4*z-1)*(9*z+4)**2/(4*(1+9*z**2)**3)
    hg=(1+9*z**2)**(-mp.mpf(1)/4)*mp.hyper([mp.mpf(1)/12,mp.mpf(5)/12],[1],ch)
    sr=mp.fsum(mp.mpf(A[n])*(z/4)**n for n in range(700))
    assert abs(hg-sr)<mp.mpf('1e-55')



# Birational elliptic normalization and Ramanujan transformation (page 2).
u,v=sp.symbols('u v')
sqrt3=sp.sqrt(3)
p_uv=(v-u)/(2*sqrt3)
q_uv=(u+v)/2
Auv=u**2/sp.Integer(4)+u/sp.Integer(2)+sp.Rational(1,3)
Buv=u**2/sp.Integer(2)+u/sp.Integer(3)
Cuv=u**2/sp.Integer(3)-a
Fuv=sp.factor(F.subs({p:p_uv,q:q_uv})-a)
assert sp.factor(Fuv-(Auv*v**2+Buv*v+Cuv))==0
Duv=sp.factor(Buv**2-4*Auv*Cuv)
quartic_alpha=-x**4+(2+12*a)*x**2+4*a-1
assert sp.factor(12*Duv.subs(u,x-1)-quartic_alpha)==0
assert sp.factor(sp.discriminant(quartic_alpha,x)+4096*a**2*(4*a-1)*(9*a+4)**2)==0
assert sp.factor(sp.discriminant(quartic_alpha,x).subs(a,sp.Rational(2,3))) != 0

# Generic branch-point map to Legendre-Jacobi form.
AA,BB,XX=sp.symbols('AA BB XX', nonzero=True)
kk=(AA-BB)/(AA+BB)
x_of_X=BB*(XX+kk)/(XX-kk)
quartic=sp.factor((AA**2-x_of_X**2)*(x_of_X**2-BB**2))
VV2=sp.factor((XX-kk)**4*quartic/(4*BB**2*(AA-BB)**2))
assert sp.factor(VV2-XX*(XX-1)*(XX-kk**2))==0
w_factor=2*BB*(AA-BB)/(XX-kk)**2
assert sp.factor(sp.diff(x_of_X,XX)/w_factor + 1/(AA+BB))==0

# Alpha-dependent branch parameter, j-map, and gauge identities.
r=sp.sqrt(1-4*a)
m_alpha=sp.factor((1+6*a-r)/(1+6*a+r))
S2=2*(1+6*a+r)  # (AA+BB)^2 on the real branch
assert sp.factor(S2**2*(1-m_alpha+m_alpha**2)-16*(1+9*a**2))==0
X_alpha=sp.factor(27*m_alpha**2*(1-m_alpha)**2/(4*(1-m_alpha+m_alpha**2)**3))
assert sp.simplify(X_alpha-chi)==0

# Exact chain-rule proof of the (1/2,1/2) -> (1/12,5/12) map.
m=sp.symbols('m')
Dm=1-m+m**2
Xm=sp.factor(27*m**2*(1-m)**2/(4*Dm**3))
hm=Dm**sp.Rational(1,4)
G0,G1=sp.symbols('G0 G1')
G2=(sp.Rational(1,4)*G0-(1-2*m)*G1)/(m*(1-m))
Ym=sp.diff(hm,m)*G0+hm*G1
Ymm=sp.diff(hm,m,2)*G0+2*sp.diff(hm,m)*G1+hm*G2
Xmp=sp.diff(Xm,m); Xmpp=sp.diff(Xmp,m)
YX=Ym/Xmp
YXX=(Ymm*Xmp-Ym*Xmpp)/Xmp**3
ram_L=sp.factor(sp.together(Xm*(1-Xm)*YXX+(1-sp.Rational(3,2)*Xm)*YX-sp.Rational(5,144)*hm*G0))
assert sp.factor(sp.diff(ram_L,G0))==0 and sp.factor(sp.diff(ram_L,G1))==0

# Exact signature-four pullback to the page-1 operator.
s4=sp.factor(4*a*(9*a+4)/(6*a+1)**2)
g4=(1+6*a)**(-sp.Rational(1,2))
S0,S1=sp.symbols('S0 S1')
S2=(sp.Rational(3,16)*S0-(1-2*s4)*S1)/(s4*(1-s4))
s4_y1=sp.diff(g4,a)*S0+g4*S1*sp.diff(s4,a)
s4_y2=(sp.diff(g4,a,2)*S0+2*sp.diff(g4,a)*S1*sp.diff(s4,a)
       +g4*S2*sp.diff(s4,a)**2+g4*S1*sp.diff(s4,a,2))
s4_L=sp.factor(sp.together(P2*s4_y2+P1*s4_y1+P0*g4*S0))
assert sp.factor(sp.diff(s4_L,S0))==0 and sp.factor(sp.diff(s4_L,S1))==0

# Exact quadratic transformation from signature four to the Legendre period.
zquad=sp.factor(4*m/(1+m)**2)
hquad=sp.sqrt(1+m)
Q0,Q1=sp.symbols('Q0 Q1')
Q2=(sp.Rational(1,4)*Q0-(1-2*m)*Q1)/(m*(1-m))
Yq=hquad*Q0
Yqm=sp.diff(hquad,m)*Q0+hquad*Q1
Yqmm=sp.diff(hquad,m,2)*Q0+2*sp.diff(hquad,m)*Q1+hquad*Q2
zqp=sp.diff(zquad,m); zqpp=sp.diff(zqp,m)
Yqz=Yqm/zqp
Yqzz=(Yqmm*zqp-Yqm*zqpp)/zqp**3
quad_L=sp.factor(sp.together(zquad*(1-zquad)*Yqzz+(1-2*zquad)*Yqz-sp.Rational(3,16)*Yq))
assert sp.factor(sp.diff(quad_L,Q0))==0 and sp.factor(sp.diff(quad_L,Q1))==0

# Displayed inverse plane map and invariant differential.
y_symbol=sp.symbols('y_symbol')
u_inverse=x-1
A_inverse=Auv.subs(u,u_inverse)
B_inverse=Buv.subs(u,u_inverse)
v_inverse=sp.factor((y_symbol-B_inverse)/(2*A_inverse))
q_inverse=sp.factor((u_inverse+v_inverse)/2)
p_inverse=sp.factor((v_inverse-u_inverse)/(2*sqrt3))
y_forward=sp.factor(2*Auv*v+Buv)
assert sp.simplify(q_inverse.subs({x:u+1,y_symbol:y_forward})-q_uv)==0
assert sp.simplify(p_inverse.subs({x:u+1,y_symbol:y_forward})-p_uv)==0
y_pq=sp.factor(y_forward.subs({u:q-sqrt3*p,v:q+sqrt3*p}))
assert sp.factor(sp.diff(F,p)+sqrt3*sp.diff(F,q)-2*sqrt3*y_pq)==0

# Classical K-hypergeometric normalization at independent sample points.
for mv in ['0.03','0.20','0.55','0.80']:
    mm=mp.mpf(mv)
    assert abs(mp.hyper([mp.mpf('0.5'),mp.mpf('0.5')],[1],mm)-2*mp.ellipk(mm)/mp.pi)<mp.mpf('1e-70')

# Independent Eisenstein-root check from Ramanujan's differential system.
E2s,E4s,E6s=sp.symbols('E2s E4s E6s', nonzero=True)
def RamanujanD(expr):
    return (sp.diff(expr,E2s)*(E2s**2-E4s)/12
            +sp.diff(expr,E4s)*(E2s*E4s-E6s)/3
            +sp.diff(expr,E6s)*(E2s*E6s-E4s**2)/2)
Xmod=sp.factor(1-E6s**2/E4s**3)
Gmod=E4s**sp.Rational(1,4)
DXmod=sp.factor(RamanujanD(Xmod))
GXmod=sp.factor(RamanujanD(Gmod)/DXmod)
GXXmod=sp.factor(RamanujanD(GXmod)/DXmod)
E4_L=sp.factor(sp.together(Xmod*(1-Xmod)*GXXmod+(1-sp.Rational(3,2)*Xmod)*GXmod-sp.Rational(5,144)*Gmod))
assert E4_L==0


# Exact modular turning point and high-precision slope-matched continuation.
alpha_star=(sp.sqrt(6)-2)/3
assert sp.simplify(chi.subs(a,alpha_star)-1)==0
assert sp.simplify(sp.diff(chi,a).subs(a,alpha_star))==0
assert sp.N(sp.diff(chi,a,2).subs(a,alpha_star),30)<0

def X_num(av):
    return -27*av**2*(4*av-1)*(9*av+4)**2/(4*(1+9*av**2)**3)

def AB_num(Xv):
    Acoef=mp.sqrt(mp.pi)/(mp.gamma(mp.mpf(11)/12)*mp.gamma(mp.mpf(7)/12))
    Bcoef=-2*mp.sqrt(mp.pi)/(mp.gamma(mp.mpf(1)/12)*mp.gamma(mp.mpf(5)/12))
    Aval=Acoef*mp.hyper([mp.mpf(1)/12,mp.mpf(5)/12],[mp.mpf(1)/2],1-Xv)
    Bval=Bcoef*mp.hyper([mp.mpf(11)/12,mp.mpf(7)/12],[mp.mpf(3)/2],1-Xv)
    return Aval,Bval

def continued_root_num(av):
    Xv=X_num(av); Aval,Bval=AB_num(Xv)
    astar=(mp.sqrt(6)-2)/3
    sign=mp.mpf(1) if av<=astar else mp.mpf(-1)
    return Aval+sign*mp.sqrt(1-Xv)*Bval

def direct_period_num(av):
    z=4*av*(4+9*av)/(1+6*av)**2
    return mp.hyper([mp.mpf(1)/4,mp.mpf(3)/4],[1],z)/mp.sqrt(1+6*av)

for avs in ['0.01','0.10','0.14','0.15','0.16','0.20','0.24','0.249']:
    av=mp.mpf(avs)
    Tc=continued_root_num(av)/(1+9*av**2)**(mp.mpf(1)/4)
    Td=direct_period_num(av)
    assert abs(Tc-Td)<mp.mpf('1e-60')

results = {
  'schema': 'triangle-rectangle-verification-results/1.0',
  'summary': {'status': 'PASS', 'check_count': 19},
  'checks': {
    'figure_midpoint_action_quantization': 'PASS',
    'mu_reflection_unique': 'PASS',
    'plane_operator_and_exact_certificate': 'PASS',
    'critical_points_and_abel_wick_center': 'PASS',
    'integer_period_series': 'PASS',
    'abel_wronskian_identity': 'PASS',
    'plane_birational_forward_inverse': 'PASS',
    'plane_invariant_differential': 'PASS',
    'jacobi_quartic_and_discriminant': 'PASS',
    'signature_four_ode_pullback': 'PASS',
    'legendre_birational_curve_and_differential': 'PASS',
    'signature_four_to_legendre_quadratic_pullback': 'PASS',
    'legendre_K_normalization': 'PASS',
    'alpha_m_X_parameter_chain': 'PASS',
    'legendre_to_modular_hypergeometric_pullback': 'PASS',
    'eisenstein_fourth_root_ode': 'PASS',
    'ramanujan_algebraic_factor': 'PASS',
    'modular_turning_point_exact': 'PASS',
    'piecewise_continuation_numeric': 'PASS'
  }
}
Path('verification_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')

print('ALL CHECKS PASS')
print('19 proof-level checks passed; see verification_results.json and claim_index.json for row-by-row coverage.')
