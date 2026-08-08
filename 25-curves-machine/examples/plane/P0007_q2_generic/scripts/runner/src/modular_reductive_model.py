#!/usr/bin/env python3
import argparse,json,time
from fractions import Fraction as F
import numpy as np
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators
from polynomial_hamiltonian_to_ode import mono
from modular_ode_screen_numpy import rank_mod

def energy_from_model(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E

def qmod(c,p):return (c.numerator%p)*pow(c.denominator%p,-1,p)%p
def ev(poly,a,p):
 z={}
 for (ae,pe,qe),c in poly.items():z[(pe,qe)]=(z.get((pe,qe),0)+qmod(c,p)*pow(a,ae,p))%p
 return {k:v for k,v in z.items() if v}

def screen(E,r,maxb,p,a,p_degrees=(0,2)):
 image=exact_image_map(E,r);cache=[]
 for pe in p_degrees:
  for qe in range(maxb+1):cache.append(ev(image(mono(0,pe,qe)),a,p))
 deriv=[ev(w,a,p) for w in common_derivative_numerators(E,r)];records=[]
 for b in range(maxb+1):
  idx=[]
  for ip in range(len(p_degrees)):idx += list(range(ip*(maxb+1),ip*(maxb+1)+b+1))
  exact=[cache[i] for i in idx];rows=sorted(set().union(*(x.keys() for x in exact+deriv)));pos={k:i for i,k in enumerate(rows)}
  C=np.zeros((len(rows),len(exact)),dtype=np.int64);W=np.zeros((len(rows),len(deriv)),dtype=np.int64)
  for j,x in enumerate(exact):
   for k,v in x.items():C[pos[k],j]=v
  for j,x in enumerate(deriv):
   for k,v in x.items():W[pos[k],j]=v
  rc=rank_mod(C,p);rw=rank_mod(np.hstack([C,W]),p);rel=(r+1)-(rw-rc)
  rec={'order':r,'q_bound':b,'ambient_rows':len(rows),'exact_columns':len(exact),'rank_C':rc,'rank_CW':rw,'relation_dimension':rel,'prime':p,'alpha_value':a};records.append(rec);print(rec,flush=True)
  if rel:break
 return records

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--order',type=int,default=4);ap.add_argument('--max-q',type=int,default=40);ap.add_argument('--prime',type=int,default=65521);ap.add_argument('--alpha',type=int,default=7);ap.add_argument('--output',required=True)
 ns=ap.parse_args();rec,E=energy_from_model(ns.model);out={'example_id':rec['example_id'],'records':screen(E,ns.order,ns.max_q,ns.prime,ns.alpha)};json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
if __name__=='__main__':main()
