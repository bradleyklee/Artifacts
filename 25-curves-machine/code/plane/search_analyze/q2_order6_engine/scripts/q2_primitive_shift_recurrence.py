#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys,time
from fractions import Fraction as F
from math import comb
from pathlib import Path
import numpy as np
import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

ORDER=6
BOUND=33
alpha=sp.symbols('alpha')
Qalpha=QQ.frac_field(alpha)

def log(*x): print(time.strftime('%H:%M:%S'),*x,flush=True)

def load_energy(path):
 rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
 for mons in rec['monomials'].values():
  for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
 return rec,E

def eval_qalpha_mod(x,a,p):
 expr=x.as_expr() if hasattr(x,'as_expr') else x
 num,den=sp.fraction(expr)
 nv=int(sp.Poly(num,alpha).eval(a))%p;dv=int(sp.Poly(den,alpha).eval(a))%p
 return nv*pow(dv,-1,p)%p

def pivot_columns_mod(A,p):
 A=A.copy()%p;m,n=A.shape;rank=0;piv=[]
 for c in range(n):
  nz=np.flatnonzero(A[rank:,c])
  if nz.size==0:continue
  i=rank+int(nz[0])
  if i!=rank:A[[rank,i]]=A[[i,rank]]
  inv=pow(int(A[rank,c]),-1,p);A[rank,c:]=(A[rank,c:]*inv)%p
  rows=np.flatnonzero(A[:,c]);rows=rows[rows!=rank]
  for s in range(0,len(rows),64):
   rr=rows[s:s+64];ff=A[rr,c].copy();A[rr,c:]=(A[rr,c:]-ff[:,None]*A[rank,c:][None,:])%p
  piv.append(c);rank+=1
  if rank==m:break
 return piv

def qpoly(expr):
 expr=sp.cancel(expr)
 if sp.degree(sp.denom(expr),alpha)>0:raise ValueError(('alpha denominator',expr))
 return sp.Poly(expr,alpha,domain=sp.QQ)

def qq(x): return QQ.from_sympy(sp.Rational(x))

def shifted_coeff(poly:sp.Poly,k:int,shift:int):
 if poly.is_zero:
  return QQ.zero
 deg=int(poly.degree())
 if deg<k:
  return QQ.zero
 z=sp.Rational(0)
 for e in range(k,deg+1):
  c=poly.nth(e)
  if c:z+=c*comb(e,k)*(sp.Integer(shift)**(e-k))
 return QQ.from_sympy(z)

def zero_vec(n): return DomainMatrix.zeros((n,1),QQ)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True);ap.add_argument('--src',type=Path,required=True);ap.add_argument('--operator-verified',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--shift',type=int,default=7);ap.add_argument('--prime',type=int,default=65521);ap.add_argument('--max-degree',type=int,default=80);ap.add_argument('--inverse-only',action='store_true')
 ns=ap.parse_args();sys.path.insert(0,str(ns.src))
 from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators,to_qalpha_rows,sparse_from_qalpha_coefficients,verify_identity,DerivedRelation
 from polynomial_hamiltonian_to_ode import mono,der,power,curve_reducer
 rec,E=load_energy(ns.model);op=json.load(open(ns.operator_verified));ints=list(map(int,op['primitive_integer_coefficients']))
 Ps=[sum(sp.Integer(ints[j*32+e])*alpha**e for e in range(32)) for j in range(ORDER+1)]
 labels=[(i,j) for i in range(4) for j in range(BOUND-i+1)]
 log('BUILD_START')
 image=exact_image_map(E,ORDER);Cc=[to_qalpha_rows(image(mono(0,i,j))) for i,j in labels];Wc=[to_qalpha_rows(w) for w in common_derivative_numerators(E,ORDER)];rows=sorted(set().union(*(Cc+Wc)))
 log('BUILD_DONE','rows',len(rows),'columns',len(labels))
 # Gauge out the known constant primitive kernel rho^(2r-1).
 rho=der(E,1);_,reduce_curve=curve_reducer(E);K=to_qalpha_rows(reduce_curve(power(rho,2*ORDER-1)))
 candidates=[]
 for lab in labels:
  x=K.get(lab,Qalpha.zero)
  if x:
   ex=sp.cancel(x.as_expr())
   if sp.degree(ex,alpha)==0 and sum(lab)==BOUND:candidates.append((lab,ex))
 omit_label,omit_coeff=candidates[0];omit=labels.index(omit_label);keep=[i for i in range(len(labels)) if i!=omit]
 pos={r:i for i,r in enumerate(rows)};Cm=np.zeros((len(rows),len(keep)),dtype=np.int64)
 for jj,ci in enumerate(keep):
  for row,x in Cc[ci].items():Cm[pos[row],jj]=eval_qalpha_mod(x,ns.shift,ns.prime)
 if len(pivot_columns_mod(Cm,ns.prime))!=len(keep):raise RuntimeError('bad column gauge')
 pivrows=pivot_columns_mod(Cm.T,ns.prime)
 if len(pivrows)!=len(keep):raise RuntimeError('bad row pivots')
 log('GAUGE_PIVOTS_PASS','omit',omit_label,'kernel_coeff',omit_coeff,'rank',len(keep))
 # Build exact polynomial entries only for square pivot system and RHS.
 cp=[[qpoly(Cc[ci].get(rows[ri],Qalpha.zero).as_expr()) for ci in keep] for ri in pivrows]
 # RHS W*P at pivot rows.
 bp=[]
 for ri in pivrows:
  row=rows[ri];ex=sp.Integer(0)
  for j in range(ORDER+1):
   w=Wc[j].get(row,Qalpha.zero)
   if w:ex+=w.as_expr()*Ps[j]
  bp.append(qpoly(ex))
 maxc=max(x.degree() for row in cp for x in row if not x.is_zero);maxb=max(x.degree() for x in bp if not x.is_zero)
 log('POLY_DATA_READY','C_degree',maxc,'rhs_degree',maxb)
 n=len(keep);s=ns.shift
 A0=DomainMatrix.from_list([[shifted_coeff(cp[i][j],0,s) for j in range(n)] for i in range(n)],QQ)
 A1=DomainMatrix.from_list([[shifted_coeff(cp[i][j],1,s) for j in range(n)] for i in range(n)],QQ)
 A2=DomainMatrix.from_list([[shifted_coeff(cp[i][j],2,s) for j in range(n)] for i in range(n)],QQ)
 bcoef=[]
 for k in range(maxb+1):bcoef.append(DomainMatrix.from_list([[shifted_coeff(bp[i],k,s)] for i in range(n)],QQ))
 log('INVERSE_START')
 t=time.time();invnum,invden=A0.inv_den();log('INVERSE_DONE','seconds',time.time()-t,'den_digits',len(str(abs(int(invden)))))
 if ns.inverse_only:
  ns.output.write_text(json.dumps({'status':'INVERSE_PASS','matrix_size':n,'inverse_denominator':str(invden),'inverse_denominator_digits':len(str(abs(int(invden)))),'omit_label':list(omit_label),'pivot_rows':[list(rows[i]) for i in pivrows]},indent=2)+'\n');return
 vs=[];z=zero_vec(n)
 for k in range(ns.max_degree+1):
  rhs=bcoef[k] if k<len(bcoef) else z
  if k>=1:rhs=rhs-A1*vs[k-1]
  if k>=2:rhs=rhs-A2*vs[k-2]
  vk=(invnum*rhs)/invden
  vs.append(vk)
  nz=sum(1 for x in vk.to_list_flat() if x)
  maxdigits=max((len(str(abs(int(x.numerator)))) for x in vk.to_list_flat() if x),default=0)
  log('COEFF',k,'nonzero',nz,'max_num_digits',maxdigits)
  if k>maxb+2 and not any(vk.to_list_flat()) and not any(vs[k-1].to_list_flat()):
   log('RECURRENCE_TERMINATED','degree',k-2);break
 else:raise RuntimeError('polynomial recurrence did not terminate')
 # Convert beta=(alpha-shift) expansion to alpha polynomials.
 vals=[]
 for i in range(n):
  ex=sp.Integer(0)
  for k,vk in enumerate(vs):
   x=vk[i,0].element
   if x:ex+=sp.Rational(x.numerator,x.denominator)*(alpha-s)**k
  vals.append(sp.expand(ex))
 coeffs={labels[ci]:sp.factor(v) for ci,v in zip(keep,vals) if v!=0}
 # Exact full rectangular check at the polynomial level using the original columns.
 for row in rows:
  lhs=sp.Integer(0)
  for lab,v in coeffs.items():
   x=Cc[labels.index(lab)].get(row,Qalpha.zero)
   if x:lhs+=x.as_expr()*v
  rhs=sp.Integer(0)
  for j in range(ORDER+1):
   x=Wc[j].get(row,Qalpha.zero)
   if x:rhs+=x.as_expr()*Ps[j]
  if sp.expand(lhs-rhs)!=0:raise AssertionError(('row residual',row,sp.factor(lhs-rhs)))
 log('RECTANGULAR_CHECK_PASS')
 V=sparse_from_qalpha_coefficients(coeffs)
 rel=DerivedRelation(order=ORDER,primitive_q_degree=BOUND,rational_operator=Ps,polynomial_operator=Ps,primitive_coefficients=coeffs,primitive_numerator=V,exact_column_count=len(labels),exact_rank=len(keep),quotient_dimension=len(rows)-len(keep),combined_rank=len(keep)+ORDER,row_count=len(rows),pivot_rows=[rows[i] for i in pivrows],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='shifted_energy_recurrence')
 log('SPARSE_VERIFY_START');t=time.time();verify_identity(E,rel);vsec=time.time()-t;log('SPARSE_VERIFY_PASS','seconds',vsec)
 out={'example_id':rec['example_id'],'status':'EXACT_ORDER6_DIFFERENTIAL_CERTIFICATE_PASS','method':'shifted_energy_coefficient_recurrence','shift':s,'order':ORDER,'source_weight_bound':BOUND,'rows':len(rows),'source_columns':len(labels),'exact_rank':len(keep),'omit_label':list(omit_label),'omit_kernel_coefficient':str(omit_coeff),'operator_integer_sha256':op['integer_coefficient_sha256'],'primitive_nonzero_blocks':len(coeffs),'primitive_expanded_terms':len(V),'primitive_max_alpha_degree':max(a for a,p,q in V),'primitive_max_source_weight':max(p+q for a,p,q in V),'primitive_coefficients':{f'p^{p} q^{q}':str(sp.expand(v)) for (p,q),v in coeffs.items()},'primitive_terms':[{'alpha_degree':a,'p_degree':p,'q_degree':q,'coefficient':str(c)} for (a,p,q),c in sorted(V.items())],'pivot_rows':[list(rows[i]) for i in pivrows],'inverse_denominator':str(invden),'verify_seconds':vsec}
 text=json.dumps(out,indent=2)+'\n';ns.output.write_text(text);log('CERTIFICATE_WRITTEN','bytes',len(text),'sha256',hashlib.sha256(text.encode()).hexdigest())
if __name__=='__main__':main()
