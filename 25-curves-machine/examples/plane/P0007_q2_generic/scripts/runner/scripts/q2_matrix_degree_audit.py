#!/usr/bin/env python3
import json,sys
from fractions import Fraction as F
from pathlib import Path
import sympy as sp
alpha=sp.symbols('alpha')
ROOT=Path('/mnt/data/quartic_transfer_work/extracted/semi_random_quartics_2026-08-02')
sys.path.insert(0,str(ROOT/'src'))
from cartesian_cohomology_reduction import exact_image_map,common_derivative_numerators,to_qalpha_rows
from polynomial_hamiltonian_to_ode import mono
rec=json.load(open(ROOT/'models/q2_generic.json'))
E={(0,2,0):F(1),(0,0,2):F(1)}
for mons in rec['monomials'].values():
    for pe,qe,c in mons:E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
out=[]
for r in range(1,7):
    B=6*r-3
    labels=[(i,j) for i in range(4) for j in range(B-i+1)]
    C=[to_qalpha_rows(exact_image_map(E,r)(mono(0,i,j))) for i,j in labels]
    W=[to_qalpha_rows(w) for w in common_derivative_numerators(E,r)]
    def degs(cols):
        nd=[];dd=[]
        for col in cols:
            for x in col.values():
                ex=sp.cancel(x.as_expr())
                num,den=sp.fraction(ex)
                nd.append(sp.degree(num,alpha));dd.append(sp.degree(den,alpha))
        return int(max(nd,default=0)),int(max(dd,default=0))
    cd=degs(C);wd=degs(W)
    rows=len(set().union(*(C+W)))
    out.append({'order':r,'B':B,'rows':rows,'C_columns':len(C),'W_columns':len(W),'C_num_degree':cd[0],'C_den_degree':cd[1],'W_num_degree':wd[0],'W_den_degree':wd[1]})
    print(out[-1],flush=True)
Path('/mnt/data/quartic_transfer_work/drill/q2_matrix_degree_audit.json').write_text(json.dumps(out,indent=2)+'\n')
