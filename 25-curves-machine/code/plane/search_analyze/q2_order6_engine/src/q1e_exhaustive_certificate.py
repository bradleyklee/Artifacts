#!/usr/bin/env python3
from fractions import Fraction as F
import json,time,sys
import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy import QQ
from modular_reductive_model import energy_from_model
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators,to_qalpha_rows,Qalpha,alpha,primitive_polynomial_operator,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation
from polynomial_hamiltonian_to_ode import mono

REC,E=energy_from_model('../models/q1e.json')

def labels(r):
 b=5*r-2
 return [(0,q) for q in range(b+1)] + [(2,q) for q in range(b-1)]

def matrices(r):
 labs=labels(r);im=exact_image_map(E,r)
 Cc=[to_qalpha_rows(im(mono(0,p,q))) for p,q in labs]
 Wc=[to_qalpha_rows(w) for w in common_derivative_numerators(E,r)]
 rows=sorted(set().union(*(Cc+Wc)))
 C=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Cc] for row in rows],Qalpha)
 W=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Wc] for row in rows],Qalpha)
 return labs,rows,C,W

def symbol_check():
 n=sp.symbols('n')
 checks=[]
 for r in range(1,7):
  im=exact_image_map(E,r)
  for N in (23,29,31,37):
   cs=[to_qalpha_rows(im(mono(0,0,N))),to_qalpha_rows(im(mono(0,2,N-2)))]
   rs=[(0,N+4),(2,N+2)]
   M=sp.Matrix([[cs[j].get(row,Qalpha.zero).as_expr() for j in range(2)] for row in rs])
   expected=sp.Rational(8,25)*(N-(5*r-2))*(2*N-(10*r-5))
   assert sp.expand(M.det()-expected)==0
  checks.append({'order':r,'symbol_minor':str(sp.Rational(8,25)*(n-(5*r-2))*(2*n-(10*r-5))),'stopping_weight':5*r-2})
 return checks

def main():
 t0=time.time();syms=symbol_check();rank_table=[];derived=None
 for r in range(1,5):
  labs,rows,C,W=matrices(r);A=DomainMatrix.hstack(C,W);rc=C.rank();ra=A.rank();rel=(r+1)-(ra-rc)
  rec={'order':r,'stopping_weight':5*r-2,'rows':len(rows),'exact_columns':len(labs),'rank_C':rc,'rank_CW':ra,'relation_dimension':rel};rank_table.append(rec);print(rec,flush=True)
  if r==4:
   ns=A.nullspace().to_Matrix();assert ns.rows==1
   row=list(ns.row(0));nC=len(labs);rat=[sp.factor(x) for x in row[nC:]];top=next(x for x in reversed(rat) if sp.simplify(x)!=0);row=[sp.factor(x/top) for x in row];rat=row[nC:]
   P,scale=primitive_polynomial_operator(rat);coeffs={lab:sp.factor(-scale*x) for lab,x in zip(labs,row[:nC]) if sp.simplify(x)!=0};V=sparse_from_qalpha_coefficients(coeffs)
   D=DerivedRelation(order=4,primitive_q_degree=18,rational_operator=rat,polynomial_operator=P,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=len(labs),exact_rank=rc,quotient_dimension=len(rows)-rc,combined_rank=ra,row_count=len(rows),pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='triangular_weight')
   verify_identity(E,D)
   old=json.load(open('../data/q1e_exact_reductive.json'));oldP=[sp.sympify(x) for x in old['operator_coefficients']];assert all(sp.expand(x-y)==0 for x,y in zip(P,oldP))
   oldV={(z['alpha_degree'],z['p_degree'],z['q_degree']):F(z['coefficient']) for z in old['primitive_terms']};assert V==oldV
   derived={'operator_coefficients':[str(sp.expand(x)) for x in P],'operator_factored':[str(sp.factor(x)) for x in P],'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(x)) for (p,q),x in coeffs.items()},'primitive_terms':[{'alpha_degree':a,'p_degree':p,'q_degree':q,'coefficient':str(c)} for (a,p,q),c in sorted(V.items())],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'max_source_weight':max(p+q for p,q in coeffs),'status':'EXHAUSTIVE_CERTIFICATE_PASS'}
 assert [x['relation_dimension'] for x in rank_table]==[0,0,0,1]
 out={'example_id':'q1e','E':REC['E'],'symbol_checks':syms,'rank_table':rank_table,'derived':derived,'elapsed_seconds':time.time()-t0,'status':'EXHAUSTIVE_CERTIFICATE_PASS'}
 json.dump(out,open('../data/q1e_exhaustive_certificate.json','w'),indent=2);open('../data/q1e_exhaustive_certificate.json','a').write('\n')
 print('EXHAUSTIVE_CERTIFICATE_PASS',derived['primitive_nonzero_blocks'],derived['primitive_expanded_terms'],'sec',out['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
