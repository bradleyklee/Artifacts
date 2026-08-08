from fractions import Fraction as Q
from itertools import product, combinations
from math import gcd
from functools import reduce
import sys,json,time
import sympy as sp
sys.path.insert(0,'/mnt/data/_quartic_work/semi_random_quartics_2026-08-02/src')
from general_quartic_series import series
from guess_ode import guess
sys.path.insert(0,'/mnt/data/quartic_mode_search_2026-08-02/src')
from build_candidates import symmetries,R2

a=sp.symbols('alpha')

def normop(ps):
 expr=[]
 for p in ps:
  z=sum(sp.Rational(v.numerator,v.denominator)*a**e for e,v in p.items());expr.append(sp.Poly(z,a,domain=sp.QQ))
 den=sp.ilcm(*[int(c.q) for P in expr for c in P.all_coeffs()]) if any(P.all_coeffs() for P in expr) else 1
 ints=[]
 for P in expr: ints.extend([int(c*den) for c in P.all_coeffs()])
 g=reduce(gcd,[abs(x) for x in ints if x],0) or 1
 out=[sp.expand(P.as_expr()*den/g) for P in expr]
 if sp.Poly(out[-1],a).LC()<0:out=[-x for x in out]
 return out

def score(op):
 coeffs=[]
 for x in op:coeffs += [int(c) for c in sp.Poly(x,a).all_coeffs()]
 return (max(len(str(abs(c))) for c in coeffs if c),sum(1 for c in coeffs if c),sum(len(str(abs(c))) for c in coeffs if c))

def mk_spec(c3,c4):
 return {'3':[[3-i,i,str(c)] for i,c in enumerate(c3) if c], '4':[[4-i,i,str(c)] for i,c in enumerate(c4) if c]}

def poly(c3,c4):
 E=dict(R2)
 for i,c in enumerate(c3):
  if c:E[(3-i,i)]=c
 for i,c in enumerate(c4):
  if c:E[(4-i,i)]=c
 return E

results=[];t=time.time()
# all nonzero cubic coefficient vectors in {-1,0,1}/5, modulo overall sign canonical first nonzero positive
for vv in product([-1,0,1],repeat=4):
 if not any(vv):continue
 first=next(x for x in vv if x)
 if first<0:continue
 c3=[Q(x,5) for x in vv];c4=[Q(0)]*5
 try:seq=series(mk_spec(c3,c4),45);ans=guess(seq,max_order=2,max_degree=7,holdout=10)
 except Exception:continue
 if not ans or ans[0]!=2:continue
 op=normop(ans[2]); sy=symmetries(poly(c3,c4))
 results.append({'family':'cubic','coeffs':vv,'degree':ans[1],'operator':[str(x) for x in op],'score':score(op),'symmetry_count':len(sy),'symmetries':sy})
# quartic disabled
if False:
 indices=range(5)
 for k in [2,3,4,5]:
  for supp in combinations(indices,k):
   for signs in product([-1,1],repeat=k):
    if signs[0]<0:continue
    vv=[0]*5
    for i,s in zip(supp,signs):vv[i]=s
    c3=[Q(0)]*4;c4=[Q(x,4) for x in vv]
    try:seq=series(mk_spec(c3,c4),45);ans=guess(seq,max_order=2,max_degree=8,holdout=10)
    except Exception:continue
    if not ans or ans[0]!=2:continue
    op=normop(ans[2]);sy=symmetries(poly(c3,c4))
    results.append({'family':'quartic','coeffs':vv,'degree':ans[1],'operator':[str(x) for x in op],'score':score(op),'symmetry_count':len(sy),'symmetries':sy})
results.sort(key=lambda r:(r['score'],r['symmetry_count'],r['coeffs']))
out={'seconds':time.time()-t,'count':len(results),'top':results[:50]}
open('/mnt/data/quartic_order2_locus_2026-08-02/simple_exact_search.json','w').write(json.dumps(out,indent=2)+'\n')
for fam in ['cubic','quartic']:
 print('\n',fam)
 xs=[r for r in results if r['family']==fam]
 for r in xs[:12]: print(r['coeffs'],r['degree'],r['score'],'sym',r['symmetry_count'],r['operator'])
print('total',len(results),'sec',time.time()-t)
