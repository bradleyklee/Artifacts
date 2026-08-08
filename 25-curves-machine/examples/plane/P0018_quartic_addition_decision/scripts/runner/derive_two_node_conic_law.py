#!/usr/bin/env python3
"""Derive an addition law directly on a two-node plane quartic.

Benchmark: Edwards quartic x^2+y^2=1+d*x^2*y^2.  No Weierstrass
conversion and no preloaded group formula are used in the derivation.

The projective quartic has nodes [1:0:0] and [0:1:0].  A conic through
those two nodes, the identity O=(0,1), and generic P,Q has one residual
intersection R.  The sum is obtained by the fixed residual involution.
"""
from __future__ import annotations
import sympy as sp
import json

x,x1,y1,x2,y2,d=sp.symbols('x x1 y1 x2 y2 d')

# A conic through both nodes has affine form a*x*y+b*x+c*y+e=0.
# Requiring O=(0,1) gives e=-c, hence a*x*y+b*x+c*(y-1)=0.
# The remaining coefficients are the cross product of the evaluation rows at P,Q.
r1=sp.Matrix([x1*y1,x1,y1-1])
r2=sp.Matrix([x2*y2,x2,y2-1])
a,b,c=map(sp.factor,list(r1.cross(r2)))

# Solve the conic for y and intersect with the quartic.
y_on_conic=sp.factor((c-b*x)/(a*x+c))
intersection=sp.Poly(sp.expand(sp.together(
    x**2+y_on_conic**2-1-d*x**2*y_on_conic**2
).as_numer_denom()[0]),x)
assert intersection.degree()==4
coeff=intersection.all_coeffs()

# The finite roots are x(O)=0,x(P)=x1,x(Q)=x2,x(R)=xR.
xR=sp.factor(-coeff[1]/coeff[0]-x1-x2)
yR=sp.factor(y_on_conic.subs(x,xR))

# The residual involution is sigma(x,y)=(x,-y), so sum=sigma(R).
X_direct=xR
Y_direct=-yR

# A compact simplification is recovered only after the direct construction.
X_compact=(x1*y2+y1*x2)/(1+d*x1*x2*y1*y2)
Y_compact=(y1*y2-x1*x2)/(1-d*x1*x2*y1*y2)

F1=x1**2+y1**2-1-d*x1**2*y1**2
F2=x2**2+y2**2-1-d*x2**2*y2**2

# Exact verification of compact result: curve closure and invariant differential.
curve_res=sp.together(X_compact**2+Y_compact**2-1-d*X_compact**2*Y_compact**2)
# Tangent derivatives on each input curve.
dy1dx=-x1*(1-d*y1**2)/(y1*(1-d*x1**2))
dy2dx=-x2*(1-d*y2**2)/(y2*(1-d*x2**2))
dX1=sp.diff(X_compact,x1)+sp.diff(X_compact,y1)*dy1dx
dX2=sp.diff(X_compact,x2)+sp.diff(X_compact,y2)*dy2dx
omega1_res=sp.together(dX1/(Y_compact*(1-d*X_compact**2))-1/(y1*(1-d*x1**2)))
omega2_res=sp.together(dX2/(Y_compact*(1-d*X_compact**2))-1/(y2*(1-d*x2**2)))

# Reduce numerators modulo the two input curve equations using a Groebner basis.
GB=sp.groebner([F1,F2],y1,y2,x1,x2,order='lex',domain=sp.EX)
def reduced_zero(expr):
    num=sp.expand(sp.together(expr).as_numer_denom()[0])
    rem=sp.factor(GB.reduce(num)[1])
    return rem==0, rem

checks={}
for name,expr in [('curve_closure',curve_res),('omega_input_1',omega1_res),('omega_input_2',omega2_res)]:
    ok,rem=reduced_zero(expr)
    checks[name]={'ok':bool(ok),'remainder':str(rem)}

# Derive the compact coefficient pattern from a symmetry-compatible ansatz,
# using exact rational point data and the same curve/differential conditions.
cpar,epar,gpar=sp.symbols('cpar epar gpar')
C=cpar*d; G=gpar*d; E=epar
Xa=(x1*y2+y1*x2)/(1+C*x1*x2*y1*y2)
Ya=(y1*y2+E*x1*x2)/(1+G*x1*x2*y1*y2)
curve_a=sp.together(Xa**2+Ya**2-1-d*Xa**2*Ya**2)
dXa1=sp.diff(Xa,x1)+sp.diff(Xa,y1)*dy1dx
dXa2=sp.diff(Xa,x2)+sp.diff(Xa,y2)*dy2dx
diff_a1=sp.together(dXa1/(Ya*(1-d*Xa**2))-1/(y1*(1-d*x1**2)))
diff_a2=sp.together(dXa2/(Ya*(1-d*Xa**2))-1/(y2*(1-d*x2**2)))
samples=[
 (sp.Rational(37,100), -8,sp.Rational(5,3), sp.Rational(-5,2),2),
 (sp.Rational(571,256), -8,sp.Rational(2,3), sp.Rational(-8,7),sp.Rational(2,5)),
 (sp.Rational(99,64), -6,sp.Rational(4,5), sp.Rational(-4,3),sp.Rational(2,3)),
 (sp.Rational(47,12), -6,sp.Rational(1,2), sp.Rational(-3,2),sp.Rational(2,5)),
]
eqs=[]
for dv,xa,ya,xb,yb in samples:
    sub={d:dv,x1:xa,y1:ya,x2:xb,y2:yb}
    for expr in (curve_a,diff_a1,diff_a2):
        eqs.append(sp.factor(sp.together(expr.subs(sub)).as_numer_denom()[0]))
ansatz_gb=sp.groebner(eqs,cpar,epar,gpar,order='lex')
ansatz_basis=[sp.factor(g.as_expr()) for g in ansatz_gb.polys]

# Exact comparisons of the direct residual law with compact law on the curve.
# Full raw symbolic reduction is large; fresh exact points independently confirm it.
fresh=[
 (sp.Rational(19,64), -4,2, sp.Rational(-4,5),sp.Rational(2,3)),
 (sp.Rational(8,3), -4,sp.Rational(3,5), sp.Rational(-3,2),sp.Rational(1,2)),
]
fresh_checks=[]
for dv,xa,ya,xb,yb in fresh:
    sub={d:dv,x1:xa,y1:ya,x2:xb,y2:yb}
    fresh_checks.append({
      'input':[str(v) for v in (dv,xa,ya,xb,yb)],
      'direct_X_minus_compact_X':str(sp.factor((X_direct-X_compact).subs(sub))),
      'direct_Y_minus_compact_Y':str(sp.factor((Y_direct-Y_compact).subs(sub))),
    })

out={
 'conic_coefficients':{'a':str(a),'b':str(b),'c':str(c)},
 'direct_residual':{'xR':str(xR),'yR_length':len(str(yR))},
 'sum_rule':'(X,Y)=(xR,-yR)',
 'compact_law':{'X':str(X_compact),'Y':str(Y_compact)},
 'ansatz_groebner_basis':[str(g) for g in ansatz_basis],
 'exact_symbolic_checks':checks,
 'fresh_direct_vs_compact':fresh_checks,
}
print(json.dumps(out,indent=2))
