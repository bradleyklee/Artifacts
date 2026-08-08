#!/usr/bin/env python3
import json,time,sys
import sympy as sp
from q1_model import energy_sparse
from cartesian_cohomology_reduction import build_attempt,relation_rows,primitive_polynomial_operator,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation

E=energy_sparse();r=6;b=31
t0=time.time();a=build_attempt(E,r,b,p_degrees=(0,2));t_build=time.time()-t0
print('BUILD_DONE',t_build,'rows',len(a.rows),'C',a.exact_columns,'nullity',a.combined_nullspace.shape[0],flush=True)
good=relation_rows(a);assert len(good)==1
row=good[0];n=a.exact_columns
rat=[sp.factor(x) for x in row[n:]]
highest=next(x for x in reversed(rat) if sp.simplify(x)!=0)
row=[sp.factor(x/highest) for x in row];rat=row[n:]
P,scale=primitive_polynomial_operator(rat)
coeffs={label:sp.factor(-scale*x) for label,x in zip(a.primitive_labels,row[:n]) if sp.simplify(x)!=0}
V=sparse_from_qalpha_coefficients(coeffs)
# Direct sparse verification without quotient audit.
rel=DerivedRelation(order=r,primitive_q_degree=b,rational_operator=rat,polynomial_operator=P,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=a.exact_columns,exact_rank=a.exact_columns,quotient_dimension=len(a.rows)-a.exact_columns,combined_rank=a.combined_rank,row_count=len(a.rows),pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='not_computed')
t1=time.time();verify_identity(E,rel);t_verify=time.time()-t1
out={
 'example_id':'semi_random_quartic_q1_p_even','order':r,'primitive_q_degree':b,
 'rows':len(a.rows),'exact_columns':a.exact_columns,'combined_rank':a.combined_rank,'combined_nullity':a.combined_nullspace.shape[0],
 'build_seconds':t_build,'verify_seconds':t_verify,
 'operator_coefficients':[str(sp.expand(x)) for x in P],
 'operator_factored':[str(sp.factor(x)) for x in P],
 'operator_degrees':[sp.degree(x,sp.symbols('alpha')) for x in P],
 'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),
 'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(x)) for (p,q),x in coeffs.items()},
 'primitive_terms':[{'alpha_degree':aa,'p_degree':pp,'q_degree':qq,'coefficient':str(c)} for (aa,pp,qq),c in sorted(V.items())],
 'status':'EXACT_REDUCTIVE_PASS'
}
json.dump(out,open('../data/q1_exact_reductive.json','w'),indent=2);open('../data/q1_exact_reductive.json','a').write('\n')
print('EXACT_REDUCTIVE_PASS','Pdegrees',out['operator_degrees'],'blocks',len(coeffs),'terms',len(V),'verify',t_verify,flush=True)
