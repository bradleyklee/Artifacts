#!/usr/bin/env python3
import argparse,json,time
from fractions import Fraction as F
import sympy as sp
from cartesian_cohomology_reduction import build_attempt,relation_rows,primitive_polynomial_operator,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation

def energy_from_model(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E

def main():
 ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('--order',type=int,required=True);ap.add_argument('--q-bound',type=int,required=True);ap.add_argument('--output',required=True)
 ns=ap.parse_args();rec,E=energy_from_model(ns.model);r=ns.order;b=ns.q_bound
 t0=time.time();a=build_attempt(E,r,b,p_degrees=(0,2));build=time.time()-t0
 print('BUILD_DONE',build,'rows',len(a.rows),'C',a.exact_columns,'nullity',a.combined_nullspace.shape[0],flush=True)
 good=relation_rows(a);assert len(good)==1
 row=good[0];n=a.exact_columns;rat=[sp.factor(x) for x in row[n:]];highest=next(x for x in reversed(rat) if sp.simplify(x)!=0);row=[sp.factor(x/highest) for x in row];rat=row[n:]
 P,scale=primitive_polynomial_operator(rat);coeffs={lab:sp.factor(-scale*x) for lab,x in zip(a.primitive_labels,row[:n]) if sp.simplify(x)!=0};V=sparse_from_qalpha_coefficients(coeffs)
 rel=DerivedRelation(order=r,primitive_q_degree=b,rational_operator=rat,polynomial_operator=P,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=a.exact_columns,exact_rank=a.exact_columns,quotient_dimension=len(a.rows)-a.exact_columns,combined_rank=a.combined_rank,row_count=len(a.rows),pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='not_computed')
 t1=time.time();verify_identity(E,rel);verify=time.time()-t1
 out={'example_id':rec['example_id'],'order':r,'primitive_q_degree':b,'rows':len(a.rows),'exact_columns':a.exact_columns,'combined_rank':a.combined_rank,'combined_nullity':a.combined_nullspace.shape[0],'build_seconds':build,'verify_seconds':verify,'operator_coefficients':[str(sp.expand(x)) for x in P],'operator_factored':[str(sp.factor(x)) for x in P],'operator_degrees':[int(sp.degree(x,sp.symbols('alpha'))) for x in P],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(x)) for (p,q),x in coeffs.items()},'primitive_terms':[{'alpha_degree':aa,'p_degree':pp,'q_degree':qq,'coefficient':str(c)} for (aa,pp,qq),c in sorted(V.items())],'status':'EXACT_REDUCTIVE_PASS'}
 json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n');print('EXACT_REDUCTIVE_PASS',out['operator_degrees'],len(coeffs),len(V),verify,flush=True)
if __name__=='__main__':main()
