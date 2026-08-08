#!/usr/bin/env python3
import argparse,json,time,sys,os
from fractions import Fraction as F
import sympy as sp
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'semi_random_quartics/src'))
from cartesian_cohomology_reduction import build_attempt,relation_rows,primitive_polynomial_operator,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation

def energy_from_model(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E
ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--order',type=int,required=True);ap.add_argument('--q-bound',type=int,required=True);ap.add_argument('--output',required=True);ap.add_argument('--p-degrees',default='');ns=ap.parse_args()
rec,E=energy_from_model(ns.model);t=time.time();pds=None if not ns.p_degrees else tuple(map(int,ns.p_degrees.split(',')));a=build_attempt(E,ns.order,ns.q_bound,p_degrees=pds);bt=time.time()-t
print('built',len(a.rows),a.exact_columns,a.combined_nullspace.shape,bt,flush=True)
good=relation_rows(a);print('good',len(good),flush=True);assert len(good)==1
row=good[0];n=a.exact_columns;rat=[sp.factor(x) for x in row[n:]];highest=next(x for x in reversed(rat) if sp.simplify(x)!=0);row=[sp.factor(x/highest) for x in row];rat=row[n:]
P,scale=primitive_polynomial_operator(rat)
coeffs={lab:sp.factor(-scale*x) for lab,x in zip(a.primitive_labels,row[:n]) if sp.simplify(x)!=0}

V={}
alpha=sp.symbols('alpha')
for (pp,qq),expr in coeffs.items():
 poly=sp.Poly(sp.cancel(expr),alpha,domain=sp.QQ)
 for (aa,),cc in poly.terms():
  if cc: V[(aa,pp,qq)]=F(int(cc.p),int(cc.q))
rel=DerivedRelation(order=ns.order,primitive_q_degree=ns.q_bound,rational_operator=rat,polynomial_operator=P,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=a.exact_columns,exact_rank=-1,quotient_dimension=-1,combined_rank=a.combined_rank,row_count=len(a.rows),pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='none')
t=time.time();verify_identity(E,rel);vt=time.time()-t
out={'example_id':rec['example_id'],'status':'EXACT_REDUCTIVE_PASS','order':ns.order,'q_bound':ns.q_bound,'rows':len(a.rows),'exact_columns':a.exact_columns,'combined_rank':a.combined_rank,'nullspace_rows':a.combined_nullspace.shape[0],'build_seconds':bt,'verify_seconds':vt,'operator_coefficients':[str(sp.expand(x)) for x in P],'operator_factored':[str(sp.factor(x)) for x in P],'operator_degrees':[int(sp.degree(x,sp.symbols('alpha'))) for x in P],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(x)) for (p,q),x in coeffs.items()}}
json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n');print('PASS',out['operator_degrees'],len(coeffs),len(V),vt,flush=True)
