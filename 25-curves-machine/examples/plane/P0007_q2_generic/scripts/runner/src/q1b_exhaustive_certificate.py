#!/usr/bin/env python3
from fractions import Fraction as F
import json,time,math
import sympy as sp
from sympy.polys.matrices import DomainMatrix
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators,to_qalpha_rows,Qalpha,primitive_polynomial_operator,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation
from polynomial_hamiltonian_to_ode import mono
from modular_reductive_model import energy_from_model
REC,E=energy_from_model('../models/q1b.json')

def symbol_poly(r,n):return sp.Rational(2,9)*(11*n*n-(96*r-46)*n+198*r*r-195*r+48)
def stopping(r):
 n=sp.symbols('n');roots=sp.nroots(11*n*n-(96*r-46)*n+198*r*r-195*r+48)
 return math.floor(max(float(sp.re(x)) for x in roots))
def labels(r):
 b={1:3,2:8,3:13,4:21}[r];return [(0,q) for q in range(b+1)]+[(2,q) for q in range(max(0,b-1))]
def matrices(r):
 labs=labels(r);im=exact_image_map(E,r);Cc=[to_qalpha_rows(im(mono(0,p,q))) for p,q in labs];Wc=[to_qalpha_rows(w) for w in common_derivative_numerators(E,r)];rows=sorted(set().union(*(Cc+Wc)));C=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Cc] for row in rows],Qalpha);W=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Wc] for row in rows],Qalpha);return labs,rows,C,W

def main():
 t0=time.time();checks=[]
 for r in range(1,7):
  im=exact_image_map(E,r)
  for N in (23,29,31,37):
   cs=[to_qalpha_rows(im(mono(0,0,N))),to_qalpha_rows(im(mono(0,2,N-2)))];rs=[(0,N+4),(2,N+2)];M=sp.Matrix([[cs[j].get(row,Qalpha.zero).as_expr() for j in range(2)] for row in rs]);assert sp.expand(M.det()-symbol_poly(r,N))==0
  checks.append({'order':r,'symbol_minor':str(sp.factor(symbol_poly(r,sp.symbols('n')))),'largest_symbol_root_floor':stopping(r)})
 rank=[];derived=None
 for r in range(1,5):
  labs,rows,C,W=matrices(r);A=DomainMatrix.hstack(C,W);rc=C.rank();ra=A.rank();reld=(r+1)-(ra-rc);z={'order':r,'stopping_weight':{1:3,2:8,3:13,4:21}[r],'rows':len(rows),'exact_columns':len(labs),'rank_C':rc,'rank_CW':ra,'relation_dimension':reld};rank.append(z);print(z,flush=True)
  if r==4:
   ns=A.nullspace().to_Matrix();assert ns.rows==1;row=list(ns.row(0));nc=len(labs);rat=[sp.factor(x) for x in row[nc:]];top=next(x for x in reversed(rat) if sp.simplify(x)!=0);row=[sp.factor(x/top) for x in row];rat=row[nc:];P,scale=primitive_polynomial_operator(rat);coeffs={lab:sp.factor(-scale*x) for lab,x in zip(labs,row[:nc]) if sp.simplify(x)!=0};V=sparse_from_qalpha_coefficients(coeffs);D=DerivedRelation(order=4,primitive_q_degree=21,rational_operator=rat,polynomial_operator=P,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=nc,exact_rank=rc,quotient_dimension=len(rows)-rc,combined_rank=ra,row_count=len(rows),pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='triangular_weight');verify_identity(E,D)
   series=json.load(open('../data/q1b_operator_order4_processed.json'));Q=[sp.sympify(x) for x in series['primitive_integer_operator']];assert all(sp.expand(x-y)==0 for x,y in zip(P,Q))
   derived={'operator_coefficients':[str(sp.expand(x)) for x in P],'operator_factored':[str(sp.factor(x)) for x in P],'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(x)) for (p,q),x in coeffs.items()},'primitive_terms':[{'alpha_degree':a,'p_degree':p,'q_degree':q,'coefficient':str(c)} for (a,p,q),c in sorted(V.items())],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'max_source_weight':max(p+q for p,q in coeffs),'status':'EXHAUSTIVE_CERTIFICATE_PASS'}
 assert [x['relation_dimension'] for x in rank]==[0,0,0,1]
 out={'example_id':'q1b','E':REC['E'],'symbol_checks':checks,'rank_table':rank,'derived':derived,'elapsed_seconds':time.time()-t0,'status':'EXHAUSTIVE_CERTIFICATE_PASS'};json.dump(out,open('../data/q1b_exhaustive_certificate.json','w'),indent=2);open('../data/q1b_exhaustive_certificate.json','a').write('\n');print('EXHAUSTIVE_CERTIFICATE_PASS',derived['primitive_nonzero_blocks'],derived['primitive_expanded_terms'],out['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
