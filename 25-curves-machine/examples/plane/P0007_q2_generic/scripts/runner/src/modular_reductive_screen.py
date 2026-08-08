#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from fractions import Fraction as F
import numpy as np
from q1_model import energy_sparse
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators
from polynomial_hamiltonian_to_ode import mono,curve_reducer
from modular_ode_screen_numpy import rank_mod

def qmod(c,p):
 return (c.numerator%p)*pow(c.denominator%p,-1,p)%p

def eval_poly(poly,a,p):
 out={}
 for (ae,pe,qe),c in poly.items():
  v=qmod(c,p)*pow(a,ae,p)%p
  k=(pe,qe);out[k]=(out.get(k,0)+v)%p
 return {k:v for k,v in out.items() if v}

def attempt(E,r,b,p,a,p_degrees=(0,2)):
 image=exact_image_map(E,r)
 exact=[];labels=[]
 for pe in p_degrees:
  for qe in range(b+1):
   labels.append((pe,qe));exact.append(eval_poly(image(mono(0,pe,qe)),a,p))
 deriv=[eval_poly(w,a,p) for w in common_derivative_numerators(E,r)]
 rows=sorted(set().union(*(c.keys() for c in exact+deriv)))
 C=np.zeros((len(rows),len(exact)),dtype=np.int64);W=np.zeros((len(rows),len(deriv)),dtype=np.int64)
 pos={k:i for i,k in enumerate(rows)}
 for j,c in enumerate(exact):
  for k,v in c.items():C[pos[k],j]=v
 for j,c in enumerate(deriv):
  for k,v in c.items():W[pos[k],j]=v
 rc=rank_mod(C,p);rw=rank_mod(np.hstack([C,W]),p)
 rel=(r+1)-(rw-rc)
 return {'order':r,'q_bound':b,'prime':p,'alpha_value':a,'ambient_rows':len(rows),'exact_columns':len(exact),'rank_C':rc,'rank_CW':rw,'relation_dimension':rel}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--max-order',type=int,default=6);ap.add_argument('--max-q',type=int,default=40);ap.add_argument('--prime',type=int,default=65521);ap.add_argument('--alpha',type=int,default=7);ap.add_argument('--output')
 ns=ap.parse_args();E=energy_sparse();records=[]
 for r in range(1,ns.max_order+1):
  for b in range(ns.max_q+1):
   t=time.time();rec=attempt(E,r,b,ns.prime,ns.alpha);rec['seconds']=round(time.time()-t,4);records.append(rec);print(rec,flush=True)
   if rec['relation_dimension']>0:break
 out={'example_id':'semi_random_quartic_q1_p_even','method':'modular evaluation of exact-image/derivative matrices','records':records}
 if ns.output:json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
if __name__=='__main__':main()
