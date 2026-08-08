from fractions import Fraction as Q
from itertools import product,combinations
from math import gcd
from functools import reduce
import sys,json,time,sympy as sp
sys.path.insert(0,'/mnt/data/_quartic_work/semi_random_quartics_2026-08-02/src')
from general_quartic_series import series
from guess_ode import guess
sys.path.insert(0,'/mnt/data/quartic_mode_search_2026-08-02/src')
from build_candidates import symmetries,R2
A=sp.symbols('alpha')
def normop(ps):
 es=[sp.Poly(sum(sp.Rational(v.numerator,v.denominator)*A**e for e,v in p.items()),A,domain=sp.QQ) for p in ps]
 den=1
 for P in es:
  for c in P.all_coeffs():den=sp.ilcm(den,int(c.q))
 vals=[int(c*den) for P in es for c in P.all_coeffs()];g=reduce(gcd,[abs(x) for x in vals if x],0) or 1
 out=[sp.expand(P.as_expr()*den/g) for P in es]
 if sp.Poly(out[-1],A).LC()<0:out=[-x for x in out]
 return out
def score(op):
 cs=[int(c) for x in op for c in sp.Poly(x,A).all_coeffs() if c]
 return (max(len(str(abs(c))) for c in cs),len(cs),sum(len(str(abs(c))) for c in cs))
def spec(v):return {'3':[],'4':[[4-i,i,str(Q(x,4))] for i,x in enumerate(v) if x]}
def poly(v):
 E=dict(R2)
 for i,x in enumerate(v):
  if x:E[(4-i,i)]=Q(x,4)
 return E
res=[];t=time.time()
for k in [2,3]:
 for supp in combinations(range(5),k):
  for signs in product([-1,1],repeat=k):
   if signs[0]<0:continue
   v=[0]*5
   for i,s in zip(supp,signs):v[i]=s
   try:ans=guess(series(spec(v),36),max_order=2,max_degree=8,holdout=7)
   except Exception:continue
   if ans and ans[0]==2:
    op=normop(ans[2]);sy=symmetries(poly(v));res.append({'coeffs':v,'degree':ans[1],'operator':[str(x) for x in op],'score':score(op),'symmetries':sy})
res.sort(key=lambda x:(x['score'],len(x['symmetries']),x['coeffs']))
open('/mnt/data/quartic_order2_locus_2026-08-02/simple_quartic_exact_search.json','w').write(json.dumps({'seconds':time.time()-t,'count':len(res),'results':res},indent=2)+'\n')
for x in res[:20]:print(x['coeffs'],x['degree'],x['score'],'sym',len(x['symmetries']),x['operator'])
print('count',len(res),'sec',time.time()-t)
