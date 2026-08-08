#!/usr/bin/env python3
"""Coefficient-dependent bounds for polynomial quartic Hamiltonians.

For E(p,q) of degree <= 4, let F4 be the homogeneous degree-four part.
After an SL(2,Q) coordinate change, assume a40=[p^4]F4 != 0.
For the order-r exact-image map with m=2r-1, the associated-graded
map A_n -> A_{n+5}, A=Q[p,q]/(F4), has determinant

    Disc(F4)^2 / a40^4 * (n - 3m)^4.

Thus when Disc(F4) != 0, source total degree B_r=6r-3 is exhaustive.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction as F
import sympy as sp

p,q=sp.symbols('p q')

def load_model(path):
    rec=json.load(open(path))
    E=p**2+q**2
    for mons in rec.get('monomials',{}).values():
        for pe,qe,c in mons:
            E += sp.Rational(c)*p**int(pe)*q**int(qe)
    return rec,sp.expand(E)

def homogeneous_part(E,d):
    P=sp.Poly(E,p,q,domain=sp.QQ)
    return sp.Add(*[c*p**i*q**j for (i,j),c in P.terms() if i+j==d])

def binary_quartic_coefficients(F4):
    P=sp.Poly(F4,p,q,domain=sp.QQ)
    return tuple(P.coeff_monomial(p**i*q**(4-i)) for i in range(4,-1,-1))

def discriminant_binary_quartic(coeffs):
    a,b,c,d,e=coeffs
    x=sp.symbols('x')
    return sp.factor(sp.discriminant(a*x**4+b*x**3+c*x**2+d*x+e,x))

def choose_axis(F4):
    # Find a small rational vector (A,C) with F4(A,C) != 0.
    candidates=[]
    for height in range(0,9):
        for A in range(-height,height+1):
            for C in range(-height,height+1):
                if max(abs(A),abs(C))!=height or (A,C)==(0,0):
                    continue
                if sp.expand(F4.subs({p:A,q:C}))!=0:
                    # Complete first column (A,C) to an SL(2,Q) matrix.
                    if A!=0: B,D=sp.Integer(0),sp.Rational(1,A)
                    else: B,D=sp.Rational(-1,C),sp.Integer(0)
                    return {'A':str(A),'B':str(B),'C':str(C),'D':str(D)}
    raise ValueError('degree-four part is identically zero')

def transformed_quartic(F4,T):
    A,B,C,D=map(sp.Rational,(T[k] for k in ('A','B','C','D')))
    P,Q=sp.symbols('P Q')
    z=sp.expand(F4.subs({p:A*P+B*Q,q:C*P+D*Q}, simultaneous=True))
    return sp.expand(z.subs({P:p,Q:q}))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--max-order',type=int,default=9); ap.add_argument('--output',required=True)
    ns=ap.parse_args(); rec,E=load_model(ns.model); F4=homogeneous_part(E,4)
    if F4==0: raise SystemExit('not a genuine quartic')
    T=choose_axis(F4); G4=transformed_quartic(F4,T); coeffs=binary_quartic_coefficients(G4); a40=coeffs[0]; disc=discriminant_binary_quartic(coeffs)
    regular=(a40!=0 and disc!=0)
    orders=[]
    for r in range(1,ns.max_order+1):
        B=6*r-3
        source_cols=4*B-2 # p-residues 0..3, total degree <= B
        row_bound=4*(B+5)-2
        orders.append({'order':r,'primitive_denominator_power':2*r-1,'source_weight_bound':B if regular else None,'source_column_bound':source_cols if regular else None,'ambient_row_bound':row_bound if regular else None,'combined_column_bound':source_cols+r+1 if regular else None})
    out={'example_id':rec.get('example_id'),'E':str(E),'degree4_part':str(F4),'sl2_transform_old_from_new':T,'transformed_degree4_part':str(G4),'binary_quartic_coefficients':[str(x) for x in coeffs],'a40':str(a40),'discriminant':str(disc),'squarefree_at_infinity':bool(disc!=0),'uniform_symbol_determinant':'Disc(F4)^2/a40^4 * (n-(6*r-3))^4','uniform_bound_status':'PROVED' if regular else 'DEGENERATE_INFINITY_FALLBACK_REQUIRED','order_bounds':orders}
    json.dump(out,open(ns.output,'w'),indent=2); open(ns.output,'a').write('\n'); print(out['uniform_bound_status'],out['discriminant'])
if __name__=='__main__':main()
