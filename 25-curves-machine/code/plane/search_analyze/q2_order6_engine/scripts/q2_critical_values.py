import json,sympy as sp,time
p,q,a=sp.symbols('p q alpha')
rec=json.load(open('/mnt/data/quartic_transfer_work/extracted/semi_random_quartics_2026-08-02/models/q2_generic.json'))
E=p**2+q**2
for mons in rec['monomials'].values():
 for pe,qe,c in mons:E+=sp.Rational(c)*p**int(pe)*q**int(qe)
print('start',flush=True);t=time.time()
G=sp.groebner([sp.diff(E,p),sp.diff(E,q),E-a],p,q,a,order='lex',domain=sp.QQ)
print('groebner_sec',time.time()-t,'len',len(G.polys),flush=True)
pa=[sp.Poly(g.as_expr(),a,domain=sp.QQ) for g in G.polys if not (g.as_expr().has(p) or g.as_expr().has(q))]
print('alpha_polys',len(pa),[(x.degree(),x.LC()) for x in pa],flush=True)
for x in pa:print(sp.factor(x.as_expr()),flush=True)
