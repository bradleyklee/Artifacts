#!/usr/bin/env python3
import json,time,argparse
from fractions import Fraction as F
from cartesian_cohomology_reduction import build_attempt,relation_rows

def energy_from_model(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E
ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--spec',default='1:5,2:13,3:21');ap.add_argument('--output',required=True)
ns=ap.parse_args();rec,E=energy_from_model(ns.model);out=[]
for item in ns.spec.split(','):
 r,b=map(int,item.split(':'));t=time.time();a=build_attempt(E,r,b,p_degrees=(0,2));sec=time.time()-t;good=relation_rows(a)
 row={'order':r,'q_bound':b,'rows':len(a.rows),'exact_columns':a.exact_columns,'combined_nullity':a.combined_nullspace.shape[0],'combined_rank':a.combined_rank,'relation_dimension':len(good),'seconds':sec};out.append(row);print(row,flush=True)
json.dump({'example_id':rec['example_id'],'records':out},open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
