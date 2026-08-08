#!/usr/bin/env python3
import argparse,json,numpy as np
from fractions import Fraction as F
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators
from polynomial_hamiltonian_to_ode import mono
from modular_ode_screen_numpy import rank_mod

def energy(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E
def qmod(c,p):return c.numerator%p*pow(c.denominator%p,-1,p)%p
def ev(poly,a,p):
 z={}
 for (ae,pe,qe),c in poly.items():z[(pe,qe)]=(z.get((pe,qe),0)+qmod(c,p)*pow(a,ae,p))%p
 return {k:v for k,v in z.items() if v}
ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--order',type=int,required=True);ap.add_argument('--max-q',type=int,default=40);ap.add_argument('--prime',type=int,default=65521);ap.add_argument('--alpha',type=int,default=7);ap.add_argument('--p-degrees',default='0,1,2,3');ap.add_argument('--output',required=True);ns=ap.parse_args();rec,E=energy(ns.model);r=ns.order;pds=list(map(int,ns.p_degrees.split(',')));im=exact_image_map(E,r);cache=[]
for pe in pds:
 for q in range(ns.max_q+1):cache.append(ev(im(mono(0,pe,q)),ns.alpha,ns.prime))
der=[ev(w,ns.alpha,ns.prime) for w in common_derivative_numerators(E,r)];records=[]
for b in range(ns.max_q+1):
 idx=[]
 for ip in range(len(pds)):idx+=range(ip*(ns.max_q+1),ip*(ns.max_q+1)+b+1)
 ex=[cache[i] for i in idx];rows=sorted(set().union(*(x.keys() for x in ex+der)));pos={k:i for i,k in enumerate(rows)};C=np.zeros((len(rows),len(ex)),dtype=np.int64);W=np.zeros((len(rows),r+1),dtype=np.int64)
 for j,x in enumerate(ex):
  for k,v in x.items():C[pos[k],j]=v
 for j,x in enumerate(der):
  for k,v in x.items():W[pos[k],j]=v
 rc=rank_mod(C,ns.prime);ra=rank_mod(np.hstack([C,W]),ns.prime);rel=r+1-(ra-rc);z={'order':r,'q_bound':b,'rows':len(rows),'exact_columns':len(ex),'rank_C':rc,'rank_CW':ra,'relation_dimension':rel};records.append(z);print(z,flush=True)
 if rel:break
json.dump({'example_id':rec['example_id'],'prime':ns.prime,'alpha':ns.alpha,'p_degrees':pds,'records':records},open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
