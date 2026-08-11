#!/usr/bin/env python3
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent
payload=json.loads((HERE/'trefoil_period_payload.json').read_text())
audit=json.loads((HERE/'numerical_audit.json').read_text())
cross=json.loads((HERE/'crossing_family_view2.json').read_text())

u,E,Phi,q=sp.symbols('u E Phi q', positive=True)
h=u**2*(u+1)
lambda_coeff=sp.Rational(1,2)*(3*u**3+2*u**2)
omega_coeff=sp.diff(lambda_coeff,u)
eta=sp.simplify(omega_coeff/sp.diff(h,u))
Tpi=sp.simplify(2*eta)
assert sp.simplify(eta-(9*u+4)/(2*(3*u+2)))==0
assert sp.simplify(Tpi-(9*u+4)/(3*u+2))==0
assert sp.simplify(sp.diff(3*u**3+2*u**2,u)/sp.diff(h,u)-Tpi)==0

# Energy-native function and cubic.
phi_u=sp.simplify(3-Tpi)
assert sp.simplify(phi_u-2/(3*u+2))==0
u_phi=2*(1-Phi)/(3*Phi)
cubic=(4-27*E)*Phi**3-12*Phi+8
assert sp.simplify(cubic.subs(E,h.subs(u,u_phi)))==0

# Direct E derivatives and ODE.
dphi_dE=sp.simplify(sp.diff(phi_u,u)/sp.diff(h,u))
d2phi_dE2=sp.simplify(sp.diff(dphi_dE,u)/sp.diff(h,u))
assert sp.simplify(dphi_dE+6/(u*(3*u+2)**3))==0
assert sp.simplify(d2phi_dE2-12*(6*u+1)/(u**3*(3*u+2)**5))==0
ode=sp.factor(h*(27*h-4)*d2phi_dE2+2*(27*h-1)*dphi_dE+6*phi_u)
assert ode==0

# Gauss pullback x=27E/4: coefficient comparison after chain rule.
x=sp.symbols('x')
# E-ODE divided by the nonzero common scalar after d/dE=(27/4)d/dx.
coef2=sp.simplify((E*(27*E-4)*(sp.Rational(27,4))**2).subs(E,4*x/27))
coef1=sp.simplify((2*(27*E-1)*sp.Rational(27,4)).subs(E,4*x/27))
coef0=sp.Integer(6)
scale=sp.simplify(-coef2/(x*(1-x)))
assert sp.simplify(coef2/(-scale)-x*(1-x))==0
assert sp.simplify(coef1/(-scale)-(sp.Rational(1,2)-2*x))==0
assert sp.simplify(coef0/(-scale)+sp.Rational(2,9))==0

# Integer uniformizer is used only for the Puiseux/integral expansion.
n=sp.symbols('n', integer=True, nonnegative=True)
def a(k):
    return sp.simplify(4**k*sp.binomial(sp.Rational(3,2)*k,k))
terms=[int(a(k)) for k in range(11)]
assert terms==payload['integer_uniformizer']['first_terms_unsigned']
for k in range(9):
    assert sp.simplify((k+1)*(k+2)*a(k+2)-12*(3*k+4)*(3*k+2)*a(k))==0

# Hypergeometric branch and sign, checked in q after E=16q^2.
Hminus=sp.hyper([sp.Rational(1,3),sp.Rational(2,3)],[sp.Rational(1,2)],108*q**2) \
       -6*q*sp.hyper([sp.Rational(5,6),sp.Rational(7,6)],[sp.Rational(3,2)],108*q**2)
series_minus=sp.series(Hminus,q,0,13).removeO().expand()
series_expected=sum((-1)**k*a(k)*q**k for k in range(13))
assert sp.expand(series_minus-series_expected)==0
assert sp.expand(series_minus).coeff(q,1)==-6  # fixes the branch sign

# First positive ODE singularity.
assert sp.simplify(h.subs(u,sp.Rational(1,3))-sp.Rational(4,27))==0

# Numerical and drawing audits.
assert audit['max_relerr_constrained'] < 1e-8
assert audit['max_relerr_action_derivative'] < 1e-6
assert len(cross['records'])==8
for rec in cross['records']:
    assert rec['crossing_count']==3
    for c in rec['crossings']:
        assert abs(c['depths'][0]-c['depths'][1])>1e-8

print('PASS: restricted forms, time form, action and period')
print('PASS: energy-native cubic and second-order ODE')
print('PASS: direct Gauss pullback x=27E/4')
print('PASS: negative local branch sign and hypergeometric series')
print('PASS: A244038 integral uniformizer, terms and recurrence')
print('PASS: numerical constrained-flow and action audits')
print('PASS: eight diagrams, three strict crossings each')
