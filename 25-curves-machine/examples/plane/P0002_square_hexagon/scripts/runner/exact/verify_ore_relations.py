#!/usr/bin/env python3
"""Exact Ore-left-multiple verification for the square-hexagon ladder."""
from pathlib import Path
from math import comb
import json
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
x=sp.symbols('alpha')

def polys_from(name):
    d=json.loads((ROOT/'exact'/name).read_text())
    return d,[sp.Poly(sp.sympify(s),x,domain=sp.QQ) for s in d['polynomials']]

def normalized_fraction(s):
    e=sp.cancel(sp.sympify(s)); ne,de=sp.fraction(e)
    den=sp.Poly(de,x,domain=sp.QQ); lc=den.LC()
    return sp.Poly(ne/lc,x,domain=sp.QQ),den.monic()

def verify_relation(label,target,B,A):
    fracs=[normalized_fraction(s) for s in B]
    L=sp.Poly(1,x,domain=sp.QQ)
    for _,den in fracs: L=sp.lcm(L,den)
    lifted=[]
    for num,den in fracs:
        q,r=sp.div(L,den,domain=sp.QQ)
        assert r.is_zero
        lifted.append((num,q))
    assert len(target)==len(A)+len(B)-1
    for k in range(len(target)):
        z=sp.Poly(0,x,domain=sp.QQ)
        for i,(num,q) in enumerate(lifted):
            for j,a in enumerate(A):
                t=i+j-k
                if 0<=t<=i:
                    deriv=a.diff((x,t)) if t else a
                    z += num*q*deriv.mul_ground(comb(i,t))
        z -= target[k]*L
        assert z.is_zero,(label,k,z.degree())
    print(f'{label}: PASS (common denominator degree {L.degree()})')

def main():
    _,A4=polys_from('order4_operator.json')
    for target_file,relation_file,bkey,label in [
        ('order5_operator_and_relation.json','order5_operator_and_relation.json','left_quotient_coefficients','A5 = B1 o A4'),
        ('order6_operator.json','order6_left_quotient_by_order4.json','B_coefficients','A6 = B2 o A4'),
        ('order8_operator_and_relation.json','order8_operator_and_relation.json','left_quotient_coefficients','A8 = B4 o A4'),
        ('order12_operator_and_relation.json','order12_operator_and_relation.json','left_quotient_coefficients','A12 = B8 o A4'),
    ]:
        _,target=polys_from(target_file)
        rd=json.loads((ROOT/'exact'/relation_file).read_text())
        verify_relation(label,target,rd[bkey],A4)
    print('ORE_RELATIONS_PASS')

if __name__=='__main__': main()
