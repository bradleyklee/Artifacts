#!/usr/bin/env python3
import argparse,json,sys,numpy as np
from modular_reductive_model import energy_from_model,ev
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators
from polynomial_hamiltonian_to_ode import mono
from modular_ode_screen_numpy import rank_mod
ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--orders',default='1,2,3,4');ap.add_argument('--max-weight',type=int,default=30);ap.add_argument('--prime',type=int,default=65521);ap.add_argument('--alpha',type=int,default=7);ap.add_argument('--output',required=True)
ns=ap.parse_args();rec,E=energy_from_model(ns.model);allr=[]
for r in map(int,ns.orders.split(',')):
 im=exact_image_map(E,r);der=[ev(w,ns.alpha,ns.prime) for w in common_derivative_numerators(E,r)];records=[]
 for B in range(ns.max_weight+1):
  labs=[(0,q) for q in range(B+1)]+[(2,q) for q in range(max(0,B-1))];ex=[ev(im(mono(0,p,q)),ns.alpha,ns.prime) for p,q in labs];rows=sorted(set().union(*(x.keys() for x in ex+der)));pos={k:i for i,k in enumerate(rows)};C=np.zeros((len(rows),len(ex)),dtype=np.int64);W=np.zeros((len(rows),r+1),dtype=np.int64)
  for j,x in enumerate(ex):
   for k,v in x.items():C[pos[k],j]=v
  for j,x in enumerate(der):
   for k,v in x.items():W[pos[k],j]=v
  rc=rank_mod(C,ns.prime);ra=rank_mod(np.hstack([C,W]),ns.prime);rel=r+1-(ra-rc);z={'order':r,'weight_bound':B,'rows':len(rows),'columns':len(labs),'rank_C':rc,'rank_CW':ra,'derivative_quotient_rank':ra-rc,'relation_dimension':rel};records.append(z)
 print('order',r,'tail',records[-8:]);allr+=records
json.dump({'example_id':rec['example_id'],'prime':ns.prime,'alpha':ns.alpha,'records':allr},open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
