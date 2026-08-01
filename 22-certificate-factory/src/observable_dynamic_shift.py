#!/usr/bin/env python3
"""Full-remainder dynamic-shift certificates for A120589 and A120591."""
from __future__ import annotations
import argparse,gzip,json,math
from fractions import Fraction
from math import comb
from pathlib import Path
import sympy as sp
from expand_target_coverage import CORE,POWERS
from direct_ode_reduction import _primitive_vector
from guv_termwise_certificate_factory import expr_text
from relay_factory_v02 import recurrence_to_ode
n,u=sp.symbols("n u")

def mj(M): return [[expr_text(sp.cancel(M[i,j])) for j in range(M.cols)] for i in range(M.rows)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument("case_id");a=ap.parse_args().case_id
 root=Path(__file__).resolve().parents[1]; parent,power,_=POWERS[a];q,r,b,_=CORE[parent]
 d=Fraction(b,r-q); cs={k:Fraction(comb(q,k)*d**k,b) for k in range(2,q+1)}
 D=sp.expand(1-sum(sp.Rational(v.numerator,v.denominator)*u**(k-1) for k,v in cs.items()));rho=sp.expand(u*D)
 seed=sp.expand((1+sp.Rational(d.numerator,d.denominator)*u)**(power-1))
 aa=sp.symbols(f"a0:{q}");bb=sp.symbols(f"b0:{q}"); A=sum(aa[i]*u**i for i in range(q));B=sum(bb[i]*u**i for i in range(q))
 w=sp.expand(rho*A-sp.diff(rho,u)*B); unk=list(aa)+list(bb)
 G=sp.Matrix([[sp.diff(w.coeff(u,i),z) for z in unk] for i in range(2*q)]); assert G.det()!=0
 E=sp.zeros(2*q,q)
 for i in range(q):E[i,i]=1
 UV=G.inv()*E;U=UV[:q,:];V=UV[q:,:];J=sp.zeros(q,q)
 for j in range(1,q):J[j-1,j]=j
 assert (G*sp.Matrix.vstack(U,V)-E).is_zero_matrix
 initial=sp.Matrix([seed.coeff(u,i) for i in range(q)])
 columns=[];chains=[]
 for shift in range(q+1):
  cur=initial; steps=[]
  for k in range(shift,0,-1):
   pole=n+k-1;cv=(V*cur).applyfunc(sp.cancel);out=(U*cur-J*cv/pole).applyfunc(sp.cancel)
   steps.append((k,pole,cv));cur=out
  scale=sp.Integer(1) if shift==0 else sp.cancel(n/(n+shift))
  columns.append((scale*cur).applyfunc(sp.cancel));chains.append(steps)
 X=sp.Matrix.hstack(*columns);rank=X.to_DM(field=True).rank();ns=X.to_DM(field=True).nullspace().to_Matrix()
 assert rank==q and ns.shape==(1,q+1)
 P=_primitive_vector(list(ns[0,:]),n);assert (X*P).applyfunc(sp.cancel).is_zero_matrix
 K=q-1;N=0
 for shift in range(1,q+1):
  scale=sp.cancel(P[shift]*n/(n+shift))
  for k,pole,cv in chains[shift]:
   cp=sum(cv[i]*u**i for i in range(q))
   N+=sp.cancel(scale*cp*rho**(q-k)/(pole*seed))
 N=sp.cancel(N)
 residual=sp.expand(rho*seed*sp.diff(N,u)+rho*sp.diff(seed,u)*N-(n+K)*seed*sp.diff(rho,u)*N)
 for shift in range(q+1):
  scale=sp.cancel(P[shift]*n/(n+shift))
  residual-=seed*scale*rho**(q-shift)
 assert sp.cancel(residual)==0, sp.factor(sp.cancel(residual))
 cr=root/"examples"/a;terms=json.loads((cr/"data/terms.json").read_text())["terms"]
 checks=[sum(int(P[j].subs(n,k))*terms[k+j] for j in range(q+1)) for k in range(1,len(terms)-q)]
 assert all(v==0 for v in checks)
 ode=recurrence_to_ode(list(P),terms)
 Nt=sp.together(N);Nnum=sp.Poly(sp.numer(Nt),n,u,domain=sp.QQ)
 stats={"denominator_degree":q,"remainder_dimension":q,"shift_columns":q+1,"G_shape":[2*q,2*q],"X_shape":[q,q+1],"rank":q,"nullity":1,"recurrence_order":q,"leading_zero_coefficients":next((i for i,v in enumerate(P) if v!=0),len(P)),"certificate_numerator_degree_n":Nnum.degree(n),"certificate_numerator_degree_u":Nnum.degree(u),"certificate_parameter_denominator":expr_text(sp.denom(Nt))}
 payload={"format":"RELAY-CT-observable-dynamic-shift-v0.1","case_id":a,"D":expr_text(D),"rho":expr_text(rho),"seed":expr_text(seed),"matrices":{"G":mj(G),"U":mj(U),"V":mj(V),"J":mj(J),"X":mj(X)},"recurrence":[expr_text(v) for v in P],"certificate":{"N":expr_text(N),"denominator_base":expr_text(rho),"denominator_power":K},"ode":ode,"statistics":stats,"checks":{"GUV":True,"rank_nullity":True,"kernel":True,"cleared_certificate":True,"terms":True,"ode":ode["verification"]["series_residual"]["pass"]}}
 out=cr/"release"/"certificate_payload.json.gz"
 with gzip.open(out,"wt",encoding="utf-8",compresslevel=9) as f:json.dump(payload,f,sort_keys=True)
 for name,src in {"matrices":"matrices","recurrence":"recurrence","certificate":"certificate","ode":"ode"}.items():(cr/"data"/f"{name}.json").write_text(json.dumps({"status":"verified","canonical_source":f"release/certificate_payload.json.gz#/{src}","statistics":stats},indent=2,sort_keys=True)+"\n")
 m=json.loads((cr/"manifest.json").read_text());m["case_state"]="ANALYTIC_COMPLETE"
 for name in ("matrices","recurrence","certificate","ode"):m["components"][name]={"status":"verified","canonical_path":f"data/{name}.json"}
 (cr/"manifest.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"case_id":a,"recurrence":[expr_text(v) for v in P],"statistics":stats,"payload_bytes":out.stat().st_size}))
if __name__=="__main__":main()
