#!/usr/bin/env python3
from fractions import Fraction as F
import json,time
import numpy as np
import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix
from modular_reductive_model import energy_from_model,ev
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators,to_qalpha_rows,Qalpha,alpha,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation
from polynomial_hamiltonian_to_ode import mono

REC,E=energy_from_model('../models/q1b.json');r=4;B=21
labs=[(0,q) for q in range(B+1)]+[(2,q) for q in range(B-1)]
im=exact_image_map(E,r);Cc=[to_qalpha_rows(im(mono(0,p,q))) for p,q in labs];Wc=[to_qalpha_rows(w) for w in common_derivative_numerators(E,r)];rows=sorted(set().union(*(Cc+Wc)))
C=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Cc] for row in rows],Qalpha);W=DomainMatrix.from_list([[c.get(row,Qalpha.zero) for c in Wc] for row in rows],Qalpha)
# finite-field row pivot selection
p=65521;a=7
Cm=np.zeros((len(rows),len(labs)),dtype=np.int64)
for j,c in enumerate(Cc):
 d={}
 for (pe,qe),x in c.items():
  expr=x.as_expr();num,den=sp.fraction(expr);val=(int(num.subs(alpha,a))%p)*pow(int(den.subs(alpha,a))%p,-1,p)%p;d[(pe,qe)]=val
 for k,v in d.items():Cm[rows.index(k),j]=v
A=Cm.T.copy();rank=0;piv=[]
for col in range(A.shape[1]):
 nz=np.flatnonzero(A[rank:,col])
 if nz.size==0:continue
 i=rank+int(nz[0]);A[[rank,i]]=A[[i,rank]]
 inv=pow(int(A[rank,col]),-1,p);A[rank,col:]=(A[rank,col:]*inv)%p
 rr=np.flatnonzero(A[:,col]);rr=rr[rr!=rank]
 for ii in rr:A[ii,col:]=(A[ii,col:]-int(A[ii,col])*A[rank,col:])%p
 piv.append(col);rank+=1
 if rank==len(labs):break
assert len(piv)==len(labs)
# exact operator P
op=json.load(open('../data/q1b_operator_order4_processed.json'));Ps=[sp.sympify(x) for x in op['primitive_integer_operator']]
pvec=DomainMatrix.from_list([[Qalpha.from_sympy(x)] for x in Ps],Qalpha);rhs=-(W*pvec)
# convert pivot solve to polynomial ring
R=QQ.poly_ring(alpha)
def cv(x):
 if hasattr(x,'element'):x=x.element
 return R.from_sympy(x.as_expr())
Cp=C.extract(piv,list(range(len(labs))));bp=rhs.extract(piv,[0])
Cpp=DomainMatrix.from_list([[cv(Cp[i,j]) for j in range(Cp.shape[1])] for i in range(Cp.shape[0])],R)
bpp=DomainMatrix.from_list([[cv(bp[i,0])] for i in range(bp.shape[0])],R)
t=time.time();xnum,xden=Cpp.solve_den(bpp);print('SOLVE_DONE',time.time()-t,'den degree',sp.degree(xden.as_expr(),alpha),flush=True)
xf=xnum.to_field()/xden
# full exact check
assert C*xf==rhs
coeffs={lab:sp.factor(-x.as_expr()) for lab,x in zip(labs,xf.to_list_flat()) if x}
V=sparse_from_qalpha_coefficients(coeffs)
D=DerivedRelation(order=4,primitive_q_degree=B,rational_operator=Ps,polynomial_operator=Ps,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=len(labs),exact_rank=len(labs),quotient_dimension=len(rows)-len(labs),combined_rank=46,row_count=len(rows),pivot_rows=[rows[i] for i in piv],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='modular_pivot_triangular')
verify_identity(E,D)
out={'example_id':'q1b','order':4,'source_weight_bound':B,'rows':len(rows),'exact_columns':len(labs),'pivot_rows':[list(rows[i]) for i in piv],'operator_coefficients':[str(x) for x in Ps],'primitive_coefficients':{f'p^{pp} q^{qq}':str(sp.expand(x)) for (pp,qq),x in coeffs.items()},'primitive_terms':[{'alpha_degree':aa,'p_degree':pp,'q_degree':qq,'coefficient':str(c)} for (aa,pp,qq),c in sorted(V.items())],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'max_source_weight':max(pp+qq for pp,qq in coeffs),'status':'EXACT_BACKSOLVE_CERTIFICATE_PASS'}
json.dump(out,open('../data/q1b_exact_backsolve.json','w'),indent=2);open('../data/q1b_exact_backsolve.json','a').write('\n');print('EXACT_BACKSOLVE_CERTIFICATE_PASS',len(coeffs),len(V),out['max_source_weight'],flush=True)
