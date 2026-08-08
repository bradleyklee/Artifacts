#!/usr/bin/env python3
import sympy as sp,json
p,q=sp.symbols('p q')
E=p**2+q**2+(p**4-6*p**2*q**2+q**4)/4+(3*p**2*q**3+2*q**5)/8
trans=[]
for swap in (False,True):
 for spn in (-1,1):
  for sqn in (-1,1):
   P,Q=(q,p) if swap else (p,q)
   P=spn*P;Q=sqn*Q
   if sp.expand(E.subs({p:P,q:Q}, simultaneous=True)-E)==0:
    trans.append({'swap':swap,'p_sign':spn,'q_sign':sqn,'map':f'(p,q)->({sp.sstr(P)},{sp.sstr(Q)})'})
out={'group_tested':'signed coordinate permutations (8 maps)','invariances':trans,'count':len(trans),'conclusion':'within signed coordinate permutations, only identity and p-reflection survive'}
json.dump(out,open('../symmetry_check.json','w'),indent=2);open('../symmetry_check.json','a').write('\n');print(out)
