#!/usr/bin/env python3
from fractions import Fraction as F
import json,sys
import sympy as sp
from cartesian_cohomology_reduction import DerivedRelation,verify_identity
from modular_reductive_model import energy_from_model

def relation_from_json(model_path,data_path):
 rec,E=energy_from_model(model_path);d=json.load(open(data_path));P=[sp.sympify(x) for x in (d.get('operator_coefficients') or d['derived']['operator_coefficients'])];src=d.get('primitive_terms') or d['derived']['primitive_terms'];V={(x['alpha_degree'],x['p_degree'],x['q_degree']):F(x['coefficient']) for x in src};D=DerivedRelation(order=len(P)-1,primitive_q_degree=d.get('source_weight_bound',d.get('primitive_q_degree',0)),rational_operator=P,polynomial_operator=P,primitive_coefficients={},primitive_numerator=V,exact_column_count=0,exact_rank=0,quotient_dimension=0,combined_rank=0,row_count=0,pivot_rows=[],quotient_rows=[],reduced_class_entries={},reduced_class_support=0,reduced_class_text_size=0,monomial_order='verification');verify_identity(E,D);return len(V)

def main():
 q1e=json.load(open('../data/q1e_exhaustive_certificate.json'));assert q1e['status']=='EXHAUSTIVE_CERTIFICATE_PASS';assert [x['relation_dimension'] for x in q1e['rank_table']]==[0,0,0,1];n1=relation_from_json('../models/q1e.json','../data/q1e_exhaustive_certificate.json')
 q1b=json.load(open('../data/q1b_exact_backsolve.json'));assert q1b['status']=='EXACT_BACKSOLVE_CERTIFICATE_PASS';n2=relation_from_json('../models/q1b.json','../data/q1b_exact_backsolve.json')
 for f in ('../data/q2_holdout_65521.json','../data/q2_holdout_65497.json'):
  x=json.load(open(f));assert x['training']['pass'] and x['heldout']['pass'] and x['heldout']['equations_checked']==80
 for f in ('../data/q2_modred_o6_65521_a7.json','../data/q2_modred_o6_65497_a11.json','../data/q2_modred_o6_65521_a13.json'):
  x=json.load(open(f));z=x['records'][-1];assert z['q_bound']==32 and z['relation_dimension']==1 and z['rank_C']==132 and z['rank_CW']==138
 print('SEMI_RANDOM_QUARTIC_BUNDLE_PASS',n1,n2)
if __name__=='__main__':main()
