#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,time
from fractions import Fraction as F
from pathlib import Path
import sympy as sp

def load_energy(path:Path):
    rec=json.load(open(path));E={(0,2,0):F(1),(0,0,2):F(1)}
    for mons in rec['monomials'].values():
        for pe,qe,c in mons:
            E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
    return rec,E

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--src',type=Path,required=True)
    ap.add_argument('--operator-verified',type=Path,required=True)
    ap.add_argument('--certificate',type=Path,required=True)
    ns=ap.parse_args();sys.path.insert(0,str(ns.src))
    from cartesian_cohomology_reduction import DerivedRelation,verify_identity
    rec,E=load_energy(ns.model);op=json.load(open(ns.operator_verified));cert=json.load(open(ns.certificate))
    alpha=sp.symbols('alpha');order=int(cert['order']);ints=list(map(int,op['primitive_integer_coefficients']))
    Ps=[sum(sp.Integer(ints[j*32+e])*alpha**e for e in range(32)) for j in range(order+1)]
    V={}
    for t in cert['primitive_terms']:
        V[(int(t['alpha_degree']),int(t['p_degree']),int(t['q_degree']))]=F(t['coefficient'])
    rel=DerivedRelation(
        order=order,primitive_q_degree=int(cert['source_weight_bound']),
        rational_operator=Ps,polynomial_operator=Ps,primitive_coefficients={},primitive_numerator=V,
        exact_column_count=int(cert['source_columns']),exact_rank=int(cert['exact_rank']),
        quotient_dimension=int(cert['rows'])-int(cert['exact_rank']),combined_rank=int(cert['exact_rank'])+order,
        row_count=int(cert['rows']),pivot_rows=[],quotient_rows=[],reduced_class_entries={},
        reduced_class_support=0,reduced_class_text_size=0,monomial_order='loaded_certificate')
    t=time.time();verify_identity(E,rel)
    print(json.dumps({'status':'EXACT_SPARSE_IDENTITY_PASS','example_id':rec['example_id'],'seconds':time.time()-t},indent=2))
if __name__=='__main__':main()
