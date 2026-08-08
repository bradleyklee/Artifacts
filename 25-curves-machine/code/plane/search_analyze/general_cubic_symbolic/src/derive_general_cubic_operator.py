from pathlib import Path
import sympy as sp, json, math

ROOT = Path(__file__).resolve().parents[1]
from functools import reduce
A,B,C,D,t=sp.symbols('a b c d alpha')
# Fisher ternary-cubic invariants for U=a p^3+b p^2q+c pq^2+dq^3+p^2z+q^2z-alpha z^3
c4=-16*(9*A*t*C-3*t*B**2+9*t*B*D-3*t*C**2-1)
c6=8*(729*A**2*t**2*D**2-108*A**2*t-486*A*t**2*B*C*D+108*A*t**2*C**3+108*A*t*C+108*t**2*B**3*D-27*t**2*B**2*C**2-72*t*B**2+108*t*B*D-72*t*C**2-108*t*D**2+8)
g2=sp.cancel(c4/12)
g3=sp.cancel(-c6/216)
Delta=sp.factor(g2**3-27*g3**2)
gamma=sp.factor(3*g3*sp.diff(g2,t)-2*g2*sp.diff(g3,t))
P2=sp.factor(48*Delta*gamma)
P1=sp.factor(48*(sp.diff(Delta,t)*gamma-Delta*sp.diff(gamma,t)))
P0=sp.factor(4*(sp.diff(Delta,t,2)*gamma-sp.diff(Delta,t)*sp.diff(gamma,t))-3*gamma*(g2*sp.diff(g2,t)**2-12*sp.diff(g3,t)**2))
# clear numeric denominators and polynomial content
Ps=[sp.cancel(x) for x in (P0,P1,P2)]
den=sp.lcm([sp.denom(x) for x in Ps])
raw=[sp.expand(x*den) for x in Ps]
# content gcd as multivariate polynomials
G=sp.gcd(raw[0],raw[1]); G=sp.gcd(G,raw[2]); G=sp.factor(G)
prim=[sp.factor(sp.cancel(x/G)) for x in raw]
# numeric content gcd
coeffs=[]
for p in prim:
    poly=sp.Poly(p,t,A,B,C,D,domain=sp.QQ)
    coeffs += [sp.Rational(cc) for cc in poly.coeffs()]
# normalize to integer coefficients
ld=sp.ilcm(*[int(cc.q) for cc in coeffs])
ints=[sp.expand(p*ld) for p in prim]
ig=0
for p in ints:
  for cc in sp.Poly(p,t,A,B,C,D,domain=sp.ZZ).coeffs(): ig=math.gcd(ig,abs(int(cc)))
ints=[sp.factor(p/ig) for p in ints]
if sp.Poly(ints[2],t).LC().could_extract_minus_sign(): ints=[-p for p in ints]
print('c4=',sp.factor(c4))
print('c6=',sp.factor(c6))
print('Delta=',sp.factor(Delta))
print('gamma=',sp.factor(gamma))
print('raw common factor=',G)
print('degrees alpha=',[sp.degree(p,t) for p in ints])
print('term counts=',[len(sp.Poly(sp.expand(p),t,A,B,C,D).terms()) for p in ints])
for i,p in enumerate(ints): print('P%d='%i,sp.factor(p))
# compare specialization A
vals={A:sp.Rational(1,7),B:sp.Rational(1,9),C:sp.Rational(-1,11),D:sp.Rational(1,13)}
spec=[sp.Poly(sp.expand(p.subs(vals)),t,domain=sp.QQ) for p in ints]
arch=json.loads((ROOT / 'reference/data/generic_cubic_all_A_operator_exact.json').read_text())
archp=[]
for rec in arch['coefficients']:
    archp.append(sp.Poly(sum(sp.Rational(v)*t**int(k) for k,v in rec.items()),t,domain=sp.QQ))
ratios=[]
for p,q in zip(spec,archp):
    ratios.append(sp.factor(p.as_expr()/q.as_expr()))
print('comparison ratios=',ratios)
print('same=',all(sp.simplify(r-ratios[0])==0 for r in ratios))
# save compact and expanded coeff-by-alpha
out={'definition':'H=p^2+q^2+a*p^3+b*p^2*q+c*p*q^2+d*q^3; level H=alpha; period omega=2*dq/H_p',
'c4':str(sp.factor(c4)),'c6':str(sp.factor(c6)),'Delta':str(sp.factor(Delta)),'gamma':str(sp.factor(gamma)),
'operator_factored':[str(sp.factor(p)) for p in ints],
'operator_expanded':[str(sp.expand(p)) for p in ints],
'operator_degrees_alpha':[int(sp.degree(p,t)) for p in ints],
'operator_term_counts':[len(sp.Poly(sp.expand(p),t,A,B,C,D).terms()) for p in ints],
'generic_A_comparison_ratios':[str(r) for r in ratios], 'generic_A_exact_match_up_to_scale':all(sp.simplify(r-ratios[0])==0 for r in ratios)}
(ROOT / 'data/general_cubic_order2_operator.json').write_text(json.dumps(out, indent=2) + '\n')
