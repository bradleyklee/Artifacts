#!/usr/bin/env python3
from fractions import Fraction as F
import json,sys,math
import sympy as sp
alpha=sp.symbols('alpha')
rec=json.load(open(sys.argv[1]));R=rec['order'];D=rec['degree_bound'];v=[sp.Rational(F(x).numerator,F(x).denominator) for x in rec['coefficients_flat']]
Ps=[]
for j in range(R+1):
 Ps.append(sp.expand(sum(v[j*(D+1)+e]*alpha**e for e in range(D+1))))
den=sp.ilcm(*[sp.denom(c) for P in Ps for c in sp.Poly(P,alpha).all_coeffs()])
Pis=[sp.expand(P*den) for P in Ps]
ints=[int(c) for P in Pis for c in sp.Poly(P,alpha).all_coeffs() if c]
g=abs(math.gcd(*ints));Pis=[sp.expand(P/g) for P in Pis]
if sp.Poly(Pis[-1],alpha).LC()<0:Pis=[-P for P in Pis]
out=dict(rec)
out.update({'primitive_integer_operator':[str(P) for P in Pis],'factored_operator':[str(sp.factor(P)) for P in Pis],'degrees':[int(sp.degree(P,alpha)) for P in Pis],'max_integer_digits':max(len(str(abs(int(c)))) for P in Pis for c in sp.Poly(P,alpha).all_coeffs() if c),'leading_factorization':str(sp.factor(Pis[-1]))})
json.dump(out,open(sys.argv[2],'w'),indent=2);open(sys.argv[2],'a').write('\n')
print('degrees',out['degrees'],'digits',out['max_integer_digits'])
for j,P in enumerate(Pis):print('P%d ='%j,sp.factor(P))
